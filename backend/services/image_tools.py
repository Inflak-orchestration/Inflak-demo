from __future__ import annotations

import asyncio
import base64
import io
import json
import os
import uuid
from collections import deque
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Literal

from copilot import Tool, ToolInvocation, define_tool
from pydantic import BaseModel, Field

from backend.services import chat_store, collage_asset_store, svg_collage, svg_document_manager, uploads_store


_ALLOWED_SIZES = {"1024x1024", "1536x1024", "1024x1536", "auto"}
_ALLOWED_QUALITIES = {"low", "medium", "high", "auto"}
_ALLOWED_BACKGROUNDS = {"transparent", "opaque", "auto"}
_IMAGE_API_TIMEOUT_SECONDS = float(os.getenv("OPENAI_IMAGE_TIMEOUT_SECONDS", "180"))


class GenerateImageParams(BaseModel):
    prompt: str = Field(
        description="The complete image-generation prompt compiled by the Inflak image-generation planner (subject, composition, palette, style, references)."
    )
    size: str = Field(default="1024x1024", description="Image size: 1024x1024, 1536x1024, 1024x1536, or auto.")
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")
    background: str | None = Field(default=None, description="Optional background: transparent, opaque, or auto.")
    require_transparent_background: bool = Field(
        default=False,
        description="Require a PNG with actual transparent pixels. Mandatory when generating an asset for an SVG image element.",
    )


def _has_transparent_pixels(content: bytes) -> bool:
    try:
        from PIL import Image

        with Image.open(io.BytesIO(content)) as image:
            if "A" not in image.getbands():
                return False
            alpha = image.getchannel("A")
            minimum, _maximum = alpha.getextrema()
            return minimum < 255
    except Exception:  # noqa: BLE001
        return False


def _transparent_background_unsupported(error: Exception) -> bool:
    message = str(error).lower()
    return "transparent background is not supported" in message and "background" in message


def _remove_edge_connected_white_background(content: bytes) -> bytes:
    from PIL import Image

    with Image.open(io.BytesIO(content)) as source:
        image = source.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    visited = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def is_background(x: int, y: int) -> bool:
        red, green, blue, _alpha = pixels[x, y]
        return min(red, green, blue) >= 205 and max(red, green, blue) - min(red, green, blue) <= 42

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if not visited[index] and is_background(x, y):
            visited[index] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        pixels[x, y] = (*pixels[x, y][:3], 0)
        if x > 0:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y > 0:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


class EditImageParams(BaseModel):
    image_file_id: str = Field(description="fileId (from a prior generate_image or upload) of the source image to edit.")
    prompt: str = Field(description="What to paint into the masked/target regions.")
    regions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Normalized 0..1 boxes {x, y, width, height} marking where to edit. Used when mask_file_id is absent.",
    )
    mask_file_id: str | None = Field(
        default=None, description="Optional fileId of a prebuilt PNG mask (transparent = edit area). Overrides regions."
    )
    size: str = Field(default="auto", description="Output size: 1024x1024, 1536x1024, 1024x1536, or auto.")
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")


class RestyleImageParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image to re-render in a new style.")
    style_prompt: str = Field(
        description="The target style/medium and rendering direction (e.g. 'watercolor painting', 'anime cel-shading', 'flat vector line art')."
    )
    size: str = Field(default="auto", description="Output size: 1024x1024, 1536x1024, 1024x1536, or auto.")
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")


class OutpaintImageParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image to extend.")
    prompt: str = Field(description="What content should fill the newly added area so it blends with the original.")
    direction: str = Field(default="all", description="Where to extend: all, left, right, top, or bottom.")
    size: str = Field(
        default="1536x1024",
        description="Target output size / extended canvas: 1024x1024, 1536x1024, or 1024x1536.",
    )
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")


class RemoveBackgroundParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image whose background should be removed (made transparent).")
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")


class ReplaceBackgroundParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image whose background should be replaced.")
    new_background: str = Field(description="Description of the new background/scene to place behind the main subject.")
    size: str = Field(default="auto", description="Output size: 1024x1024, 1536x1024, 1024x1536, or auto.")
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")


class GenerateVariationsParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image to generate variations of.")
    count: int = Field(default=3, description="How many variations to produce (clamped to 1..4).")
    vary_prompt: str | None = Field(
        default=None, description="Optional description of what should vary across the alternatives; omit for free variations."
    )
    size: str = Field(default="auto", description="Output size: 1024x1024, 1536x1024, 1024x1536, or auto.")
    quality: str = Field(default="high", description="Render quality: low, medium, high, or auto.")


class TransformImageParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image to transform.")
    crop_box: dict[str, Any] | None = Field(
        default=None, description="Optional normalized 0..1 crop box {x, y, width, height}, applied first."
    )
    rotate: float = Field(default=0.0, description="Rotation in degrees, counter-clockwise (also used to straighten).")
    flip: str | None = Field(default=None, description="Optional flip: horizontal or vertical.")
    resize_width: int | None = Field(
        default=None, description="Optional target width in px (height scales to keep aspect unless resize_height is set)."
    )
    resize_height: int | None = Field(default=None, description="Optional target height in px.")


class AdjustImageParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image to adjust.")
    brightness: float = Field(default=1.0, description="Brightness multiplier; 1.0 = unchanged, >1 brighter, <1 darker.")
    contrast: float = Field(default=1.0, description="Contrast multiplier; 1.0 = unchanged.")
    saturation: float = Field(default=1.0, description="Saturation multiplier; 1.0 = unchanged, 0 = grayscale.")
    sharpness: float = Field(default=1.0, description="Sharpness multiplier; 1.0 = unchanged, >1 sharper, <1 softer.")
    temperature: float = Field(
        default=0.0, description="Color temperature shift from -1.0 (cooler/blue) to 1.0 (warmer/orange); 0 = unchanged."
    )
    gamma: float = Field(default=1.0, description="Gamma; 1.0 = unchanged, <1 brightens midtones, >1 darkens.")


class ApplyFilterParams(BaseModel):
    image_file_id: str = Field(description="fileId of the source image to filter.")
    filter: str = Field(description="Filter name: grayscale, sepia, invert, blur, sharpen, or vignette.")
    strength: float = Field(default=1.0, description="Filter strength 0..1 for blur/vignette; ignored by discrete filters.")


class ComposeCollageParams(BaseModel):
    scene: dict[str, Any] = Field(
        description=(
            "Editable collage scene with canvas {width, height, background} and image layers. Each layer needs id, "
            "asset_file_id, normalized x/y/width/height, and may include crop, rotation, z_index, opacity, blend_mode, and mask."
        )
    )


class ComposeSvgCollageParams(BaseModel):
    scene: dict[str, Any] = Field(
        description=(
            "Layered SVG collage scene with canvas {width, height, background} and objects. Cutout objects reference "
            "session raster assets through asset_file_id; text objects contain text and safe style properties. Include "
            "authoring_bundle with visual_style_presets, text_authoring_options, and 1-3 pre-generated "
            "asset_candidates_by_object for every cutout. Candidate fileIds must be unique and differ from that cutout's "
            "current asset_file_id so the Artifact Canvas can render directly applicable alternatives without another AI call. "
            "For initial create-mode composition, set creation_mode to image_collage. Unless the user explicitly requests "
            "a sparse/minimal result, compose a rich poster-like first version with 4-6 cutouts and 3-5 text objects; "
            "two cutouts are only the technical minimum for an explicitly sparse scene."
        )
    )


class ExtractCollageCutoutItem(BaseModel):
    source_file_id: str = Field(description="Session fileId of the source image containing the user-confirmed object.")
    label: str = Field(min_length=1, max_length=160, description="The specific visual object to retain, for example 'orange cat' or 'red bicycle'.")
    role: Literal["character", "background", "accessory", "texture"] = Field(
        default="accessory", description="Narrative role for the cutout."
    )
    story_relation: Literal["central", "related"] = Field(default="related", description="Whether the object is central or related to the story.")
    source_region: dict[str, float] | None = Field(
        default=None,
        description="Optional normalized source region {x, y, width, height} that identifies the intended object.",
    )
    extraction_prompt: str | None = Field(default=None, description="Optional user-approved clarification for the cutout.")


class ExtractCollageCutoutsParams(BaseModel):
    items: list[ExtractCollageCutoutItem] = Field(
        min_length=1,
        max_length=8,
        description="Up to eight user-confirmed object cutout requests. Each result becomes a reviewable candidate asset.",
    )
    quality: str = Field(default="high", description="Image quality: low, medium, high, or auto.")


def _validated_cutout_region(region: dict[str, float] | None) -> dict[str, float] | None:
    if region is None:
        return None
    try:
        value = {key: float(region[key]) for key in ("x", "y", "width", "height")}
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("source_region requires numeric x, y, width, and height.") from error
    if not 0 <= value["x"] <= 1 or not 0 <= value["y"] <= 1 or not 0 < value["width"] <= 1 or not 0 < value["height"] <= 1:
        raise ValueError("source_region must use normalized 0..1 coordinates with positive width and height.")
    return value


@lru_cache(maxsize=4)
def _azure_token_provider(scope: str, tenant_id: str | None):
    from azure.identity import AzureCliCredential, get_bearer_token_provider

    credential = AzureCliCredential(tenant_id=tenant_id) if tenant_id else AzureCliCredential()
    return get_bearer_token_provider(credential, scope)


@lru_cache(maxsize=1)
def _local_config():
    try:
        from backend.services import local_config

        return local_config
    except Exception:  # noqa: BLE001
        return None


def _cfg(name: str) -> str | None:
    """Read a value from the gitignored local_config.py, ignoring blanks and the
    unfilled <...> placeholder."""
    module = _local_config()
    value = getattr(module, name, None) if module else None
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or (value.startswith("<") and value.endswith(">")):
        return None
    return value


def _make_image_client(operation: str = "generate"):
    """Return (sync_client, model_or_deployment) or an {action: error} dict.

    Defaults to Azure OpenAI with AzureCLI auth (no API key; requires `az login`).
    Set IMAGE_PROVIDER=openai (with OPENAI_API_KEY) to use OpenAI directly. The
    returned client is synchronous and is called via a thread executor so it does
    not block the event loop. `operation` selects the Azure api-version, since
    image edits require a newer preview than generations.
    """
    provider = os.getenv("IMAGE_PROVIDER", "azure").strip().lower()

    if provider != "openai":
        try:
            from openai import AzureOpenAI
        except ImportError:
            return {"action": "error", "message": "The 'openai' package is not installed. Add openai>=1.55 and reinstall."}
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or _cfg("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            return {"action": "error", "message": "Set AZURE_OPENAI_ENDPOINT in your environment or local_config.py."}
        deployment = os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT") or _cfg("AZURE_OPENAI_IMAGE_DEPLOYMENT") or "gpt-image-1.5"
        if operation == "edit":
            api_version = os.getenv("AZURE_OPENAI_IMAGE_EDIT_API_VERSION", "2025-04-01-preview")
        else:
            api_version = os.getenv(
                "AZURE_OPENAI_IMAGE_API_VERSION", os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
            )
        azure_key = os.getenv("AZURE_OPENAI_API_KEY") or _cfg("AZURE_OPENAI_API_KEY")
        auth_mode = (os.getenv("AZURE_OPENAI_AUTH") or _cfg("AZURE_OPENAI_AUTH") or "").lower()
        if auth_mode not in {"", "api_key", "azure_cli"}:
            return {
                "action": "error",
                "message": "AZURE_OPENAI_AUTH must be either 'api_key' or 'azure_cli'.",
            }
        try:
            if azure_key and auth_mode != "azure_cli":
                # API-key auth (typical for standalone Azure AI Foundry resources).
                client = AzureOpenAI(azure_endpoint=endpoint, api_key=azure_key, api_version=api_version)
            else:
                # AAD auth via Azure CLI (`az login`); needs a token for the resource's tenant.
                try:
                    import azure.identity  # noqa: F401
                except ImportError:
                    return {
                        "action": "error",
                        "message": "Set AZURE_OPENAI_API_KEY, or install azure-identity for `az login` auth.",
                    }
                scope = os.getenv("AZURE_OPENAI_SCOPE", "https://cognitiveservices.azure.com/.default")
                tenant_id = os.getenv("AZURE_OPENAI_TENANT_ID") or os.getenv("AZURE_TENANT_ID")
                client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    azure_ad_token_provider=_azure_token_provider(scope, tenant_id),
                    api_version=api_version,
                )
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not create the Azure image client: {error}"}
        return client, deployment

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"action": "error", "message": "OPENAI_API_KEY is not set; set it, or use the default Azure provider with `az login`."}
    try:
        from openai import OpenAI
    except ImportError:
        return {"action": "error", "message": "The 'openai' package is not installed. Add openai>=1.55 and reinstall."}
    client_kwargs: dict[str, Any] = {"api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url
    return OpenAI(**client_kwargs), os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")


def _extract_b64(response: Any) -> str | None:
    data = getattr(response, "data", None) or []
    return getattr(data[0], "b64_json", None) if data else None


def _png_buffer(image: Any, name: str = "image.png") -> io.BytesIO:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.name = name
    buffer.seek(0)
    return buffer


def _load_source_image(web_session: Any, image_file_id: str):
    """Return (PIL RGBA image, None) or (None, error_dict)."""
    src_path = uploads_store.upload_path(web_session.session_id, image_file_id)
    if src_path is None:
        return None, {"action": "error", "message": f"Source image {image_file_id} was not found in this session."}
    try:
        from PIL import Image
    except ImportError:
        return None, {"action": "error", "message": "The 'Pillow' package is not installed. Add Pillow>=10 and reinstall."}
    try:
        return Image.open(src_path).convert("RGBA"), None
    except Exception as error:  # noqa: BLE001
        return None, {"action": "error", "message": f"Could not open the source image: {error}"}


def _apply_vignette(image: Any, strength: float) -> Any:
    from PIL import Image, ImageDraw, ImageFilter

    base = image.convert("RGBA")
    width, height = base.size
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).ellipse([-width * 0.1, -height * 0.1, width * 1.1, height * 1.1], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=int(min(width, height) * 0.25) or 1))
    amount = max(0.0, min(1.0, strength if strength else 1.0))
    darken = mask.point(lambda v: int((255 - v) * amount))
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    base.paste(shadow, (0, 0), darken)
    return base


_COLLAGE_MAX_DIMENSION = 4096
_COLLAGE_MAX_PIXELS = 12_000_000
_COLLAGE_MAX_LAYERS = 32
_COLLAGE_BLEND_MODES = {"normal", "multiply", "screen"}
_COLLAGE_MASKS = {"rectangle", "circle"}


def _collage_number(value: Any, default: float, *, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if minimum is not None:
        number = max(minimum, number)
    if maximum is not None:
        number = min(maximum, number)
    return number


def _collage_canvas(scene: dict[str, Any]) -> tuple[int, int, tuple[int, int, int, int]] | dict[str, str]:
    from PIL import ImageColor

    canvas = scene.get("canvas")
    if not isinstance(canvas, dict):
        return {"action": "error", "message": "Collage scene requires a canvas object."}
    width = int(_collage_number(canvas.get("width"), 0, minimum=1, maximum=_COLLAGE_MAX_DIMENSION))
    height = int(_collage_number(canvas.get("height"), 0, minimum=1, maximum=_COLLAGE_MAX_DIMENSION))
    if width < 1 or height < 1 or width * height > _COLLAGE_MAX_PIXELS:
        return {"action": "error", "message": "Canvas dimensions are invalid or exceed the collage rendering limit."}
    try:
        background = ImageColor.getcolor(str(canvas.get("background", "#ffffff")), "RGBA")
    except ValueError:
        return {"action": "error", "message": "Canvas background must be a valid CSS color."}
    return width, height, background


def _collage_crop(image: Any, crop: Any) -> Any:
    if not isinstance(crop, dict):
        return image
    width, height = image.size
    x = _collage_number(crop.get("x"), 0.0, minimum=0.0, maximum=1.0)
    y = _collage_number(crop.get("y"), 0.0, minimum=0.0, maximum=1.0)
    crop_width = _collage_number(crop.get("width"), 1.0, minimum=0.0, maximum=1.0)
    crop_height = _collage_number(crop.get("height"), 1.0, minimum=0.0, maximum=1.0)
    x0, y0 = int(x * width), int(y * height)
    x1, y1 = int(min(x + crop_width, 1.0) * width), int(min(y + crop_height, 1.0) * height)
    return image.crop((x0, y0, x1, y1)) if x1 > x0 and y1 > y0 else image


def _collage_circle_mask(image: Any) -> Any:
    from PIL import Image, ImageDraw

    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, image.width - 1, image.height - 1), fill=255)
    alpha = image.getchannel("A")
    alpha = Image.composite(alpha, Image.new("L", image.size, 0), mask)
    image.putalpha(alpha)
    return image


def _collage_blend(base: Any, layer: Any, position: tuple[int, int], mode: str) -> None:
    from PIL import ImageChops

    if mode == "normal":
        base.alpha_composite(layer, dest=position)
        return
    x, y = position
    bounds = (max(0, x), max(0, y), min(base.width, x + layer.width), min(base.height, y + layer.height))
    if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
        return
    left, top, right, bottom = bounds
    source = layer.crop((left - x, top - y, right - x, bottom - y))
    destination = base.crop(bounds)
    blended = ImageChops.multiply(destination.convert("RGB"), source.convert("RGB")) if mode == "multiply" else ImageChops.screen(destination.convert("RGB"), source.convert("RGB"))
    blended_rgba = blended.convert("RGBA")
    blended_rgba.putalpha(source.getchannel("A"))
    destination.alpha_composite(blended_rgba)
    base.paste(destination, bounds)


def _render_collage_scene(web_session: Any, scene: dict[str, Any]) -> tuple[Any, dict[str, Any]] | tuple[None, dict[str, str]]:
    from PIL import Image

    canvas_definition = _collage_canvas(scene)
    if isinstance(canvas_definition, dict):
        return None, canvas_definition
    width, height, background = canvas_definition
    layers = scene.get("layers")
    if not isinstance(layers, list) or not layers:
        return None, {"action": "error", "message": "Collage scene requires at least one image layer."}
    if len(layers) > _COLLAGE_MAX_LAYERS:
        return None, {"action": "error", "message": f"Collage scene supports at most {_COLLAGE_MAX_LAYERS} layers."}

    canvas = Image.new("RGBA", (width, height), background)
    normalized_layers: list[dict[str, Any]] = []
    for index, layer in enumerate(layers):
        if not isinstance(layer, dict):
            return None, {"action": "error", "message": f"Layer {index + 1} must be an object."}
        layer_id = str(layer.get("id") or f"layer-{index + 1}")
        asset_file_id = layer.get("asset_file_id")
        if not isinstance(asset_file_id, str) or not asset_file_id:
            return None, {"action": "error", "message": f"Layer '{layer_id}' requires an asset_file_id."}
        source, error = _load_source_image(web_session, asset_file_id)
        if error:
            return None, error
        target_width = int(_collage_number(layer.get("width"), 0, minimum=0.0, maximum=1.0) * width)
        target_height = int(_collage_number(layer.get("height"), 0, minimum=0.0, maximum=1.0) * height)
        if target_width < 1 or target_height < 1:
            return None, {"action": "error", "message": f"Layer '{layer_id}' requires a positive normalized width and height."}
        normalized_layers.append({"index": index, "id": layer_id, "asset_file_id": asset_file_id, "source": source, "raw": layer, "width": target_width, "height": target_height})

    for item in sorted(normalized_layers, key=lambda value: (_collage_number(value["raw"].get("z_index"), value["index"]), value["index"])):
        raw = item["raw"]
        image = _collage_crop(item["source"], raw.get("crop"))
        image = image.resize((item["width"], item["height"]), Image.LANCZOS)
        mask = str(raw.get("mask", "rectangle")).lower()
        if mask not in _COLLAGE_MASKS:
            return None, {"action": "error", "message": f"Layer '{item['id']}' has unsupported mask '{mask}'."}
        if mask == "circle":
            image = _collage_circle_mask(image)
        opacity = _collage_number(raw.get("opacity"), 1.0, minimum=0.0, maximum=1.0)
        if opacity < 1.0:
            alpha = image.getchannel("A").point(lambda value: int(value * opacity))
            image.putalpha(alpha)
        rotation = _collage_number(raw.get("rotation"), 0.0, minimum=-360.0, maximum=360.0)
        if rotation:
            image = image.rotate(-rotation, expand=True, resample=Image.BICUBIC)
        x = int(_collage_number(raw.get("x"), 0.0, minimum=-1.0, maximum=1.0) * width)
        y = int(_collage_number(raw.get("y"), 0.0, minimum=-1.0, maximum=1.0) * height)
        blend_mode = str(raw.get("blend_mode", "normal")).lower()
        if blend_mode not in _COLLAGE_BLEND_MODES:
            return None, {"action": "error", "message": f"Layer '{item['id']}' has unsupported blend mode '{blend_mode}'."}
        _collage_blend(canvas, image, (x, y), blend_mode)

    manifest = {
        "schema_version": "1.0",
        "artifact_type": "collage-scene",
        "canvas": scene["canvas"],
        "layers": [item["raw"] for item in normalized_layers],
    }
    return canvas, manifest


async def _deliver_image(
    web_session: Any, content: bytes, *, prefix: str, caption: str, action: str
) -> dict[str, Any]:
    """Save image bytes to the session, show them in chat, and return a compact ref."""
    try:
        ref = uploads_store.save_upload(
            session_id=web_session.session_id,
            filename=f"{prefix}-{uuid.uuid4().hex}.png",
            content=content,
            mime="image/png",
        )
    except uploads_store.UploadTooLargeError:
        return {"action": "error", "message": "The resulting image exceeds the 10MB upload limit."}
    url = f"/api/sessions/{web_session.session_id}/uploads/{ref['fileId']}"
    chat_store.append_message(
        session_id=web_session.session_id,
        role="assistant",
        content=caption,
        metadata={"attachments": [ref]},
    )
    await web_session.emit({"type": "image_generated", "attachment": ref, "caption": caption, "url": url})
    return {
        "action": action,
        "fileId": ref["fileId"],
        "name": ref["name"],
        "mime": ref["mime"],
        "size": ref["size"],
        "url": url,
    }


def build_image_tools(session_ref: dict[str, Any]) -> list[Tool]:
    """Build the OpenAI image generation tool.

    The Inflak image-generation planner calls this after compiling a structured image brief.
    Azure uses Azure CLI authentication by default when no API key is configured;
    set AZURE_OPENAI_AUTH=azure_cli to force it. The generated PNG is saved to
    the session uploads, shown in the chat as an attachment, and a compact
    reference (not the base64 bytes) is returned to the model.
    """

    def _guard_tool(tool_name: str):
        """Wrap a task tool so it refuses to run unless the current pass reached
        it through L1 -> L2 (runtime layer-order enforcement)."""

        def decorator(fn):
            @wraps(fn)
            async def wrapper(params, invocation):
                web_session = session_ref.get("session")
                tracker = getattr(web_session, "layer_order", None) if web_session is not None else None
                if tracker is not None:
                    blocked = tracker.block_tool(tool_name)
                    if blocked is not None:
                        return blocked
                return await fn(params, invocation)

            return wrapper

        return decorator

    @define_tool(
        "generate_image",
        description=(
            "Generate an image with the configured OpenAI image model from a fully compiled prompt, save it to the session "
            "uploads, show it in the chat, and return a compact attachment reference. Call this only after the "
            "image brief (subject, composition, palette, style) is complete."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("generate_image")
    async def generate_image(params: GenerateImageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for image generation."}

        client_or_error = _make_image_client()
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error

        size = params.size if params.size in _ALLOWED_SIZES else "1024x1024"
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"

        prompt = params.prompt
        if params.require_transparent_background:
            prompt = f"{prompt.rstrip()} Output only the isolated complete element on a fully transparent background. No backdrop, scene, frame, shadow plane, or opaque canvas."
        request_kwargs: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "output_compression": 100,
            "output_format": "png",
            "n": 1,
        }
        if params.require_transparent_background:
            request_kwargs["background"] = "transparent"
        elif params.background in _ALLOWED_BACKGROUNDS:
            request_kwargs["background"] = params.background

        used_local_background_removal = False
        try:
            loop = asyncio.get_running_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: client.images.generate(**request_kwargs)),
                timeout=_IMAGE_API_TIMEOUT_SECONDS,
            )
        except TimeoutError:
            return {
                "action": "timeout",
                "message": f"Image generation timed out after {_IMAGE_API_TIMEOUT_SECONDS:g} seconds.",
            }
        except Exception as error:  # noqa: BLE001
            if not params.require_transparent_background or not _transparent_background_unsupported(error):
                return {"action": "error", "message": f"Image generation failed: {error}"}
            fallback_kwargs = dict(request_kwargs)
            fallback_kwargs.pop("background", None)
            fallback_kwargs["prompt"] = (
                f"{params.prompt.rstrip()} Place the isolated complete subject on a uniform pure white background "
                "that touches every image edge. No scenery, border, frame, floor, cast shadow, text, or off-white texture."
            )
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: client.images.generate(**fallback_kwargs)),
                    timeout=_IMAGE_API_TIMEOUT_SECONDS,
                )
                used_local_background_removal = True
            except TimeoutError:
                return {
                    "action": "timeout",
                    "message": f"Image generation fallback timed out after {_IMAGE_API_TIMEOUT_SECONDS:g} seconds.",
                }
            except Exception as fallback_error:  # noqa: BLE001
                return {"action": "error", "message": f"Image generation fallback failed: {fallback_error}"}

        data = getattr(response, "data", None) or []
        b64 = getattr(data[0], "b64_json", None) if data else None
        if not b64:
            return {"action": "error", "message": "The image model returned no image data."}

        try:
            content = base64.b64decode(b64)
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not decode the generated image: {error}"}
        if used_local_background_removal:
            try:
                content = _remove_edge_connected_white_background(content)
            except Exception as error:  # noqa: BLE001
                return {"action": "error", "message": f"Could not remove the generated white background: {error}"}
        if params.require_transparent_background and not _has_transparent_pixels(content):
            return {
                "action": "validation_error",
                "message": "SVG element generation requires a PNG with actual transparent background pixels.",
            }

        try:
            ref = uploads_store.save_upload(
                session_id=web_session.session_id,
                filename=f"generated-{uuid.uuid4().hex}.png",
                content=content,
                mime="image/png",
            )
        except uploads_store.UploadTooLargeError:
            return {"action": "error", "message": "The generated image exceeds the 10MB upload limit."}

        url = f"/api/sessions/{web_session.session_id}/uploads/{ref['fileId']}"
        caption = "Generated image"

        # Persist an assistant-visible message so the image survives reloads,
        # and emit a live event so the current UI renders it immediately.
        chat_store.append_message(
            session_id=web_session.session_id,
            role="assistant",
            content=caption,
            metadata={"attachments": [ref]},
        )
        await web_session.emit(
            {"type": "image_generated", "attachment": ref, "caption": caption, "url": url}
        )

        return {
            "action": "generated",
            "fileId": ref["fileId"],
            "name": ref["name"],
            "mime": ref["mime"],
            "size": ref["size"],
            "url": url,
        }

    @define_tool(
        "edit_image",
        description=(
            "Inpaint or edit an existing image with OpenAI gpt-image-1. Provide the source image fileId, an edit "
            "prompt, and either normalized regions (boxes to repaint) or a prebuilt mask fileId. The masked areas are "
            "regenerated from the prompt while the rest is kept. Saves the result, shows it in chat, and returns a ref."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("edit_image")
    async def edit_image(params: EditImageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for image editing."}

        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return {"action": "error", "message": "The 'Pillow' package is not installed. Add Pillow>=10 and reinstall."}

        src_path = uploads_store.upload_path(web_session.session_id, params.image_file_id)
        if src_path is None:
            return {"action": "error", "message": f"Source image {params.image_file_id} was not found in this session."}
        try:
            source = Image.open(src_path).convert("RGBA")
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not open the source image: {error}"}
        width, height = source.size

        if params.mask_file_id:
            mask_path = uploads_store.upload_path(web_session.session_id, params.mask_file_id)
            if mask_path is None:
                return {"action": "error", "message": f"Mask image {params.mask_file_id} was not found in this session."}
            try:
                mask = Image.open(mask_path).convert("RGBA")
                if mask.size != (width, height):
                    mask = mask.resize((width, height))
            except Exception as error:  # noqa: BLE001
                return {"action": "error", "message": f"Could not open the mask image: {error}"}
        else:
            if not params.regions:
                return {"action": "error", "message": "Provide either regions or a mask_file_id to mark the edit area."}
            mask = Image.new("RGBA", (width, height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(mask)
            for region in params.regions:
                try:
                    rx = max(0.0, min(1.0, float(region.get("x", 0))))
                    ry = max(0.0, min(1.0, float(region.get("y", 0))))
                    rw = max(0.0, min(1.0, float(region.get("width", 0))))
                    rh = max(0.0, min(1.0, float(region.get("height", 0))))
                except (TypeError, ValueError):
                    continue
                x0, y0 = int(rx * width), int(ry * height)
                x1, y1 = int(min(rx + rw, 1.0) * width), int(min(ry + rh, 1.0) * height)
                if x1 > x0 and y1 > y0:
                    draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 0))

        image_buffer = io.BytesIO()
        source.save(image_buffer, format="PNG")
        image_buffer.name = "image.png"
        image_buffer.seek(0)
        mask_buffer = io.BytesIO()
        mask.save(mask_buffer, format="PNG")
        mask_buffer.name = "mask.png"
        mask_buffer.seek(0)

        size = params.size if params.size in _ALLOWED_SIZES else "auto"
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        edit_kwargs: dict[str, Any] = {
            "model": model,
            "image": image_buffer,
            "mask": mask_buffer,
            "prompt": params.prompt,
            "size": size,
            "quality": quality,
            "n": 1,
        }
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: client.images.edit(**edit_kwargs))
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Image edit failed: {error}"}

        data = getattr(response, "data", None) or []
        b64 = getattr(data[0], "b64_json", None) if data else None
        if not b64:
            return {"action": "error", "message": "The image model returned no image data."}
        try:
            content = base64.b64decode(b64)
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not decode the edited image: {error}"}
        try:
            ref = uploads_store.save_upload(
                session_id=web_session.session_id,
                filename=f"edited-{uuid.uuid4().hex}.png",
                content=content,
                mime="image/png",
            )
        except uploads_store.UploadTooLargeError:
            return {"action": "error", "message": "The edited image exceeds the 10MB upload limit."}

        url = f"/api/sessions/{web_session.session_id}/uploads/{ref['fileId']}"
        caption = "Edited image"
        chat_store.append_message(
            session_id=web_session.session_id,
            role="assistant",
            content=caption,
            metadata={"attachments": [ref]},
        )
        await web_session.emit(
            {"type": "image_generated", "attachment": ref, "caption": caption, "url": url}
        )
        return {
            "action": "edited",
            "fileId": ref["fileId"],
            "name": ref["name"],
            "mime": ref["mime"],
            "size": ref["size"],
            "url": url,
        }

    @define_tool(
        "restyle_image",
        description=(
            "Re-render an existing image in a new style/medium (style transfer) while keeping its composition. "
            "Provide the source image fileId and a style_prompt. Saves the result, shows it in chat, returns a ref."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("restyle_image")
    async def restyle_image(params: RestyleImageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for restyling."}
        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        image_buffer = _png_buffer(source)
        size = params.size if params.size in _ALLOWED_SIZES else "auto"
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        prompt = (
            f"Re-render this image in the following style: {params.style_prompt}. "
            "Keep the original composition, subject, and layout; change only the visual style, medium, and rendering."
        )
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.images.edit(model=model, image=image_buffer, prompt=prompt, size=size, quality=quality, n=1),
            )
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Restyle failed: {error}"}
        b64 = _extract_b64(response)
        if not b64:
            return {"action": "error", "message": "The image model returned no image data."}
        try:
            content = base64.b64decode(b64)
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not decode the restyled image: {error}"}
        return await _deliver_image(web_session, content, prefix="restyled", caption="Restyled image", action="restyled")

    @define_tool(
        "outpaint_image",
        description=(
            "Extend an image beyond its original borders (outpaint). Places the source on a larger canvas and paints "
            "the added area from the prompt so it blends. Saves the result, shows it in chat, returns a ref."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("outpaint_image")
    async def outpaint_image(params: OutpaintImageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for outpainting."}
        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        from PIL import Image, ImageDraw

        target = params.size if params.size in _ALLOWED_SIZES and params.size != "auto" else "1536x1024"
        tw, th = (int(value) for value in target.split("x"))
        direction = (params.direction or "all").lower()
        fit = 0.7 if direction == "all" else 0.75
        scale = fit * min(tw / source.width, th / source.height)
        new_w, new_h = max(1, int(source.width * scale)), max(1, int(source.height * scale))
        resized = source.resize((new_w, new_h), Image.LANCZOS)
        if direction == "left":
            ox, oy = tw - new_w, (th - new_h) // 2
        elif direction == "right":
            ox, oy = 0, (th - new_h) // 2
        elif direction == "top":
            ox, oy = (tw - new_w) // 2, th - new_h
        elif direction == "bottom":
            ox, oy = (tw - new_w) // 2, 0
        else:
            ox, oy = (tw - new_w) // 2, (th - new_h) // 2
        canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        canvas.paste(resized, (ox, oy), resized)
        mask = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(mask).rectangle([ox, oy, ox + new_w, oy + new_h], fill=(255, 255, 255, 255))
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        prompt = f"Extend the image naturally to fill the surrounding empty area. {params.prompt}"
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.images.edit(
                    model=model,
                    image=_png_buffer(canvas),
                    mask=_png_buffer(mask, "mask.png"),
                    prompt=prompt,
                    size=target,
                    quality=quality,
                    n=1,
                ),
            )
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Outpaint failed: {error}"}
        b64 = _extract_b64(response)
        if not b64:
            return {"action": "error", "message": "The image model returned no image data."}
        try:
            content = base64.b64decode(b64)
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not decode the outpainted image: {error}"}
        return await _deliver_image(web_session, content, prefix="outpainted", caption="Extended image", action="outpainted")

    @define_tool(
        "remove_background",
        description=(
            "Remove the background of an image, keeping only the main subject on a transparent background. "
            "Saves the result, shows it in chat, returns a ref."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("remove_background")
    async def remove_background(params: RemoveBackgroundParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for background removal."}
        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        image_buffer = _png_buffer(source)
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        prompt = (
            "Remove the background completely. Keep only the main foreground subject with clean, precise edges, "
            "on a fully transparent background."
        )
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.images.edit(
                    model=model, image=image_buffer, prompt=prompt, size="auto", quality=quality, background="transparent", n=1
                ),
            )
        except Exception as error:  # noqa: BLE001
            return {
                "action": "error",
                "message": (
                    f"Background removal failed: {error}. The provider may not support transparent-background edits."
                ),
            }
        b64 = _extract_b64(response)
        if not b64:
            return {"action": "error", "message": "The image model returned no image data."}
        try:
            content = base64.b64decode(b64)
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not decode the cutout image: {error}"}
        return await _deliver_image(web_session, content, prefix="cutout", caption="Background removed", action="background_removed")

    @define_tool(
        "extract_collage_cutouts",
        description=(
            "Create reviewable transparent cutout assets for user-confirmed collage objects. Each request identifies a "
            "source session image and an object label. The tool saves every result as a session upload and records "
            "source, label, role, and extraction provenance in the collage asset library."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("extract_collage_cutouts")
    async def extract_collage_cutouts(params: ExtractCollageCutoutsParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for collage cutout extraction."}
        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        results: list[dict[str, Any]] = []

        for item in params.items:
            try:
                source_region = _validated_cutout_region(item.source_region)
            except ValueError as error:
                results.append(
                    {
                        "source_file_id": item.source_file_id,
                        "label": item.label,
                        "action": "failed",
                        "message": str(error),
                    }
                )
                continue
            source, error = _load_source_image(web_session, item.source_file_id)
            if error:
                results.append(
                    {
                        "source_file_id": item.source_file_id,
                        "label": item.label,
                        "action": "failed",
                        "message": error["message"],
                    }
                )
                continue

            clarification = (item.extraction_prompt or "").strip()
            region_hint = ""
            if source_region:
                region_hint = (
                    " The requested object is located near normalized source region "
                    f"x={source_region['x']}, y={source_region['y']}, "
                    f"width={source_region['width']}, height={source_region['height']}."
                )
            prompt = (
                f"Create a transparent-background collage cutout. Keep only the {item.label}; remove every other "
                "object and the complete background. Preserve the complete intended object with clean, precise edges "
                "and no added objects, text, or scenery. Output a PNG with a fully transparent background."
                f"{region_hint} {clarification}".strip()
            )
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.images.edit(
                        model=model,
                        image=_png_buffer(source),
                        prompt=prompt,
                        size="auto",
                        quality=quality,
                        background="transparent",
                        n=1,
                    ),
                )
                b64 = _extract_b64(response)
                if not b64:
                    raise ValueError("The image model returned no image data.")
                content = base64.b64decode(b64)
                cutout_ref = uploads_store.save_upload(
                    session_id=web_session.session_id,
                    filename=f"collage-cutout-{uuid.uuid4().hex}.png",
                    content=content,
                    mime="image/png",
                )
                asset, _ = collage_asset_store.save_asset(
                    web_session.session_id,
                    {
                        "source_file_id": item.source_file_id,
                        "cutout_file_id": cutout_ref["fileId"],
                        "label": item.label,
                        "role": item.role,
                        "story_relation": item.story_relation,
                        "source_region": source_region,
                        "extraction_prompt": prompt,
                        "quality": quality,
                        "status": "candidate",
                    },
                )
                results.append(
                    {
                        "asset": asset,
                        "action": "candidate_created",
                        "fileId": cutout_ref["fileId"],
                        "name": cutout_ref["name"],
                        "mime": cutout_ref["mime"],
                        "size": cutout_ref["size"],
                        "url": f"/api/sessions/{web_session.session_id}/uploads/{cutout_ref['fileId']}",
                    }
                )
            except Exception as extraction_error:  # noqa: BLE001
                failed, _ = collage_asset_store.save_asset(
                    web_session.session_id,
                    {
                        "source_file_id": item.source_file_id,
                        "label": item.label,
                        "role": item.role,
                        "story_relation": item.story_relation,
                        "source_region": source_region,
                        "extraction_prompt": prompt,
                        "quality": quality,
                        "status": "failed",
                        "failure_reason": str(extraction_error),
                    },
                )
                results.append({"asset": failed, "action": "failed", "message": str(extraction_error)})

        succeeded = [item for item in results if item["action"] == "candidate_created"]
        if succeeded:
            chat_store.append_message(
                session_id=web_session.session_id,
                role="assistant",
                content=f"Prepared {len(succeeded)} collage cutout candidate(s) for review.",
                metadata={"collageAssets": [item["asset"] for item in succeeded]},
            )
        return {"action": "collage_cutouts_extracted", "results": results, "candidate_count": len(succeeded)}

    @define_tool(
        "replace_background",
        description=(
            "Replace the background of an image with a described scene while keeping the foreground subject. "
            "Saves the result, shows it in chat, returns a ref."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("replace_background")
    async def replace_background(params: ReplaceBackgroundParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for background replacement."}
        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        image_buffer = _png_buffer(source)
        size = params.size if params.size in _ALLOWED_SIZES else "auto"
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        prompt = (
            f"Replace the background behind the main subject with: {params.new_background}. "
            "Keep the foreground subject unchanged and cleanly composited into the new scene."
        )
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.images.edit(model=model, image=image_buffer, prompt=prompt, size=size, quality=quality, n=1),
            )
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Background replacement failed: {error}"}
        b64 = _extract_b64(response)
        if not b64:
            return {"action": "error", "message": "The image model returned no image data."}
        try:
            content = base64.b64decode(b64)
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Could not decode the image: {error}"}
        return await _deliver_image(web_session, content, prefix="bg-replaced", caption="Background replaced", action="background_replaced")

    @define_tool(
        "generate_variations",
        description=(
            "Generate alternative variations of an existing image, keeping the same subject and style. Provide the "
            "source image fileId and a count (1..4). Saves each result, shows them in chat, returns their refs."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("generate_variations")
    async def generate_variations(params: GenerateVariationsParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for variations."}
        client_or_error = _make_image_client("edit")
        if isinstance(client_or_error, dict):
            return client_or_error
        client, model = client_or_error
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        image_buffer = _png_buffer(source)
        count = max(1, min(4, int(params.count)))
        size = params.size if params.size in _ALLOWED_SIZES else "auto"
        quality = params.quality if params.quality in _ALLOWED_QUALITIES else "high"
        extra = f" Vary specifically: {params.vary_prompt}." if params.vary_prompt else ""
        prompt = f"Create a creative variation of this image, keeping the same subject, style, and overall composition.{extra}"
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.images.edit(model=model, image=image_buffer, prompt=prompt, size=size, quality=quality, n=count),
            )
        except Exception as error:  # noqa: BLE001
            return {"action": "error", "message": f"Variation generation failed: {error}"}
        data = getattr(response, "data", None) or []
        if not data:
            return {"action": "error", "message": "The image model returned no image data."}
        variations: list[dict[str, Any]] = []
        for idx, item in enumerate(data):
            b64 = getattr(item, "b64_json", None)
            if not b64:
                continue
            try:
                content = base64.b64decode(b64)
            except Exception:  # noqa: BLE001
                continue
            result = await _deliver_image(
                web_session, content, prefix=f"variation-{idx + 1}", caption=f"Variation {idx + 1}", action="variation"
            )
            if result.get("action") != "error":
                variations.append({"fileId": result["fileId"], "url": result["url"]})
        if not variations:
            return {"action": "error", "message": "No variations could be produced."}
        return {"action": "variations", "count": len(variations), "variations": variations}

    @define_tool(
        "transform_image",
        description=(
            "Deterministically crop, resize, rotate, or flip an image with Pillow (no model call). Provide the source "
            "image fileId and any of: crop_box (normalized), rotate (degrees), flip, resize_width/height. Saves the "
            "result, shows it in chat, returns a ref."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("transform_image")
    async def transform_image(params: TransformImageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for image transform."}
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        from PIL import Image

        image = source
        if params.crop_box:
            width, height = image.size
            try:
                cx = max(0.0, min(1.0, float(params.crop_box.get("x", 0))))
                cy = max(0.0, min(1.0, float(params.crop_box.get("y", 0))))
                cw = max(0.0, min(1.0, float(params.crop_box.get("width", 1))))
                ch = max(0.0, min(1.0, float(params.crop_box.get("height", 1))))
            except (TypeError, ValueError):
                cx, cy, cw, ch = 0.0, 0.0, 1.0, 1.0
            x0, y0 = int(cx * width), int(cy * height)
            x1, y1 = int(min(cx + cw, 1.0) * width), int(min(cy + ch, 1.0) * height)
            if x1 > x0 and y1 > y0:
                image = image.crop((x0, y0, x1, y1))
        if params.rotate:
            image = image.rotate(float(params.rotate), expand=True, resample=Image.BICUBIC)
        if params.flip == "horizontal":
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif params.flip == "vertical":
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        if params.resize_width or params.resize_height:
            width, height = image.size
            new_w = params.resize_width or (int(width * (params.resize_height / height)) if height else width)
            new_h = params.resize_height or (int(height * (params.resize_width / width)) if width else height)
            image = image.resize((max(1, int(new_w)), max(1, int(new_h))), Image.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return await _deliver_image(web_session, buffer.getvalue(), prefix="transformed", caption="Transformed image", action="transformed")

    @define_tool(
        "adjust_image",
        description=(
            "Deterministically adjust color/tone with Pillow (no model call): brightness, contrast, saturation, "
            "sharpness, temperature (-1..1), gamma. 1.0 leaves a channel unchanged. Saves the result, shows it in chat."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("adjust_image")
    async def adjust_image(params: AdjustImageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for image adjustment."}
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        from PIL import Image, ImageEnhance

        alpha = source.split()[-1]
        rgb = source.convert("RGB")
        if params.brightness != 1.0:
            rgb = ImageEnhance.Brightness(rgb).enhance(max(0.0, params.brightness))
        if params.contrast != 1.0:
            rgb = ImageEnhance.Contrast(rgb).enhance(max(0.0, params.contrast))
        if params.saturation != 1.0:
            rgb = ImageEnhance.Color(rgb).enhance(max(0.0, params.saturation))
        if params.sharpness != 1.0:
            rgb = ImageEnhance.Sharpness(rgb).enhance(max(0.0, params.sharpness))
        if params.temperature:
            shift = max(-1.0, min(1.0, params.temperature))
            red, green, blue = rgb.split()
            red = red.point(lambda v: min(255, int(v * (1 + 0.3 * shift))))
            blue = blue.point(lambda v: max(0, int(v * (1 - 0.3 * shift))))
            rgb = Image.merge("RGB", (red, green, blue))
        if params.gamma != 1.0:
            gamma = max(0.1, params.gamma)
            lut = [min(255, int(((i / 255.0) ** gamma) * 255)) for i in range(256)]
            rgb = rgb.point(lut * 3)
        out = rgb.convert("RGBA")
        out.putalpha(alpha)
        buffer = io.BytesIO()
        out.save(buffer, format="PNG")
        return await _deliver_image(web_session, buffer.getvalue(), prefix="adjusted", caption="Adjusted image", action="adjusted")

    @define_tool(
        "apply_filter",
        description=(
            "Deterministically apply a photo filter with Pillow (no model call): grayscale, sepia, invert, blur, "
            "sharpen, or vignette. strength (0..1) controls blur/vignette. Saves the result, shows it in chat."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("apply_filter")
    async def apply_filter(params: ApplyFilterParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for filtering."}
        source, error = _load_source_image(web_session, params.image_file_id)
        if error:
            return error
        from PIL import ImageEnhance, ImageFilter, ImageOps

        name = (params.filter or "").lower()
        strength = max(0.0, min(1.0, params.strength))
        alpha = source.split()[-1]
        if name == "grayscale":
            out = ImageOps.grayscale(source.convert("RGB")).convert("RGBA")
            out.putalpha(alpha)
        elif name == "sepia":
            gray = ImageOps.grayscale(source.convert("RGB"))
            out = ImageOps.colorize(gray, black="#2e1a0a", white="#ffe9c8").convert("RGBA")
            out.putalpha(alpha)
        elif name == "invert":
            out = ImageOps.invert(source.convert("RGB")).convert("RGBA")
            out.putalpha(alpha)
        elif name == "blur":
            out = source.filter(ImageFilter.GaussianBlur(radius=1 + strength * 8))
        elif name == "sharpen":
            out = ImageEnhance.Sharpness(source.convert("RGB")).enhance(1 + strength * 3).convert("RGBA")
            out.putalpha(alpha)
        elif name == "vignette":
            out = _apply_vignette(source, strength)
        else:
            return {
                "action": "error",
                "message": f"Unknown filter '{params.filter}'. Use grayscale, sepia, invert, blur, sharpen, or vignette.",
            }
        buffer = io.BytesIO()
        out.save(buffer, format="PNG")
        return await _deliver_image(web_session, buffer.getvalue(), prefix="filtered", caption=f"{name.title()} filter", action="filtered")

    @define_tool(
        "compose_collage",
        description=(
            "Deterministically render an editable collage scene into PNG with Pillow. The scene references session image "
            "fileIds and supplies a normalized canvas plus ordered layers with crop, transform, opacity, mask, and blend mode. "
            "Saves both the rendered collage and a JSON scene manifest for later editing."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("compose_collage")
    async def compose_collage(params: ComposeCollageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for collage composition."}
        image, manifest_or_error = _render_collage_scene(web_session, params.scene)
        if image is None:
            return manifest_or_error
        try:
            manifest_ref = uploads_store.save_upload(
                session_id=web_session.session_id,
                filename=f"collage-scene-{uuid.uuid4().hex}.json",
                content=json.dumps(manifest_or_error, separators=(",", ":")).encode("utf-8"),
                mime="application/json",
            )
        except uploads_store.UploadTooLargeError:
            return {"action": "error", "message": "The collage scene manifest exceeds the upload limit."}
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        rendered = await _deliver_image(web_session, buffer.getvalue(), prefix="collage", caption="Composed collage", action="collage_composed")
        if rendered.get("action") == "error":
            return rendered
        rendered["scene_file_id"] = manifest_ref["fileId"]
        rendered["scene"] = manifest_or_error
        return rendered

    @define_tool(
        "compose_svg_collage",
        description=(
            "Compile a self-contained, layered SVG collage from session cutout assets and text objects. Every object "
            "keeps a stable id and editable transform, z-order, and text metadata. The scene should include a prepared "
            "authoring_bundle with 1-3 pre-generated replacement assets for every cutout so visual-style, "
            "asset-replacement, copy, and typography controls render with the artifact. Default initial scenes to a rich, "
            "poster-like composition with 4-6 cutouts and 3-5 text objects unless the user explicitly requests minimalism."
        ),
        skip_permission=True,
        defer="never",
    )
    @_guard_tool("compose_svg_collage")
    async def compose_svg_collage(params: ComposeSvgCollageParams, invocation: ToolInvocation) -> dict[str, Any]:
        web_session = session_ref.get("session")
        if web_session is None:
            return {"action": "error", "message": "No active web session is available for SVG collage composition."}
        try:
            content, manifest = svg_collage.compile_svg_collage(web_session.session_id, params.scene)
            ref = uploads_store.save_upload(
                session_id=web_session.session_id,
                filename=f"collage-{uuid.uuid4().hex}.svg",
                content=content,
                mime="image/svg+xml",
            )
            managed_scene = svg_document_manager.normalize_document(
                Path(ref["path"]),
                document_id=ref["fileId"],
                scene_kind_hint="collage",
                source_kind="generated",
            )
        except (svg_collage.SvgCollageError, svg_document_manager.SvgDocumentError, uploads_store.UploadTooLargeError) as error:
            return {"action": "error", "message": str(error)}
        ref["artifactType"] = "svg-document"
        ref["revision"] = managed_scene["revision"]
        ref["scene"] = managed_scene
        ref["url"] = f"/api/sessions/{web_session.session_id}/uploads/{ref['fileId']}"
        chat_store.append_message(
            session_id=web_session.session_id,
            role="assistant",
            content="Generated editable SVG collage",
            metadata={"attachments": [ref], "artifactType": "svg-document", "scene": managed_scene},
        )
        await web_session.emit({"type": "artifact_generated", "attachment": ref, "artifactType": "svg-document", "scene": managed_scene})
        return {"action": "svg_collage_composed", **ref}

    return [
        generate_image,
        edit_image,
        restyle_image,
        outpaint_image,
        remove_background,
        extract_collage_cutouts,
        replace_background,
        generate_variations,
        transform_image,
        adjust_image,
        apply_filter,
        compose_collage,
        compose_svg_collage,
    ]
