from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from backend.services import uploads_store


PLUGIN_ID = "inflak-pN9-artifact-to-structured-instruction"
REPORT_BLOCK = re.compile(r"```inflak-report\s*\n(.*?)\n```", re.DOTALL)
RENDERER = Path(__file__).with_name("render_charts.cjs")
RENDER_VERSION = "1"


def report_payload(message: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    content = str(message.get("content") or "")
    metadata = message.get("metadata") or {}
    if message.get("role") == "widget_request":
        display = (metadata.get("widget") or {}).get("display") or {}
        if isinstance(display.get("generated_report"), dict):
            return display, content
    if message.get("role") == "assistant" and not metadata.get("partial"):
        match = REPORT_BLOCK.search(content)
        if match:
            try:
                payload = json.loads(match.group(1))
            except json.JSONDecodeError:
                return None, content
            if isinstance(payload, dict) and isinstance(payload.get("generated_report"), dict):
                return payload, REPORT_BLOCK.sub("", content).strip()
    return None, content


def source_rows(session_id: str, reference: str) -> tuple[list[dict[str, Any]], bytes]:
    name = Path(str(reference)).name
    file_id = name.split("-", 1)[0]
    path = uploads_store.upload_path(session_id, file_id)
    if path is None or path.suffix.lower() != ".csv":
        return [], b""
    if path.resolve().parent != uploads_store.session_dir(session_id).resolve():
        raise ValueError("Report source must belong to this session")
    content = path.read_bytes()
    if len(content) > uploads_store.MAX_UPLOAD_BYTES:
        raise ValueError("Report source is too large")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    rows = []
    for record in reader:
        if len(rows) >= 10000:
            raise ValueError("Chart source exceeds 10000 rows; narrow the source first")
        row: dict[str, Any] = {}
        for field, value in record.items():
            if field is None or value is None:
                raise ValueError("CSV contains inconsistent rows")
            if re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
                number = float(value)
                row[field] = number if math.isfinite(number) else value
            else:
                row[field] = value
        rows.append(row)
    return rows, content


def chart_spec(chart: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    spec = chart.get("spec")
    if not rows or not isinstance(spec, dict) or not spec:
        raise ValueError("No executable chart specification or readable CSV data")
    fields = set(rows[0])
    bindings = chart.get("confirmed_field_bindings") or []
    if not bindings or any(not isinstance(field, str) or field not in fields for field in bindings):
        raise ValueError("Chart bindings do not match the source CSV")

    def validate(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"data", "datasets", "url", "href", "expr", "signal", "signals", "params", "bind"}:
                    raise ValueError(f"Unsupported chart property: {key}")
                if key == "mark" and (item == "image" or isinstance(item, dict) and item.get("type") == "image"):
                    raise ValueError("External chart images are not supported")
                validate(item)
        elif isinstance(value, list):
            for item in value:
                validate(item)

    validate(spec)
    spec = json.loads(json.dumps(spec))
    if "encoding" not in spec and not any(key in spec for key in ("layer", "hconcat", "vconcat", "facet", "repeat")):
        horizontal, vertical = spec.get("x"), spec.get("y")
        if horizontal not in fields or not isinstance(vertical, str) or vertical not in fields:
            raise ValueError("The saved chart is a recommendation, not an executable Vega-Lite specification")
        encoding = {
            "x": {"field": horizontal, "type": "ordinal"},
            "y": {"field": vertical, "type": "quantitative"},
        }
        if spec.get("color") in fields:
            encoding["color"] = {"field": spec["color"], "type": "nominal"}
        spec = {"mark": spec.get("mark", "line"), "encoding": encoding}
    spec.update({"data": {"values": rows}, "width": 620, "height": 260})
    return spec


def render_report(report: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    for field in ("title", "executive_summary"):
        if not isinstance(report.get(field), str) or not report[field].strip():
            raise ValueError(f"Report requires {field}")
    for field in ("sections", "chart_recommendations", "evidence_register", "limitations"):
        if not isinstance(report.get(field), list):
            raise ValueError(f"Report requires {field}")
    if len(report["chart_recommendations"]) > 12:
        raise ValueError("Report supports at most 12 charts")

    def text(value: Any) -> str:
        return html.escape(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))

    charts = report["chart_recommendations"]
    specs, positions, chart_results = [], [], {}
    for index, chart in enumerate(charts):
        if not isinstance(chart, dict):
            raise ValueError("Invalid chart recommendation")
        try:
            specs.append(chart_spec(chart, rows))
            positions.append(index)
        except (ValueError, TypeError) as error:
            chart_results[index] = f'<p class="notice">Chart not rendered: {text(str(error))}.</p>'
    if specs:
        try:
            node = shutil.which("node")
            if not node:
                raise ValueError("Node.js chart renderer unavailable")
            process = subprocess.run(
                [node, str(RENDERER)], input=json.dumps(specs), text=True,
                capture_output=True, timeout=30, check=True,
            )
            rendered = json.loads(process.stdout)
            if len(rendered) != len(positions):
                raise ValueError("Incomplete chart rendering")
            for index, result in zip(positions, rendered):
                chart_results[index] = result.get("svg") or f'<p class="notice">Chart not rendered: {text(result.get("error", "Invalid specification"))}.</p>'
        except (OSError, ValueError, subprocess.SubprocessError):
            for index in positions:
                chart_results[index] = '<p class="notice">Chart rendering unavailable. The analysis and chart recommendation are retained.</p>'

    sections = []
    for section in report["sections"]:
        if not isinstance(section, dict):
            raise ValueError("Invalid report section")
        sections.append(f'<section><h2>{text(section.get("heading", ""))}</h2><p>{text(section.get("content", ""))}</p><small>{text(section.get("evidence_refs", []))}</small></section>')
    figures = [f'<figure><h3>{text(chart.get("title", ""))}</h3>{chart_results[index]}<figcaption>{text(chart.get("purpose", ""))}</figcaption></figure>' for index, chart in enumerate(charts)]
    evidence = "".join(f"<li>{text(entry)}</li>" for entry in report["evidence_register"])
    limitations = "".join(f"<li>{text(entry)}</li>" for entry in report["limitations"])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<title>{text(report["title"])}</title><style>
:root{{color-scheme:light;color:#242723;background:#fff;font-family:Georgia,serif;letter-spacing:0}}
*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:960px;margin:auto;padding:28px 22px}}h1{{font-size:30px;line-height:1.2}}h2{{font-size:22px}}h3{{font-size:18px}}p,li{{line-height:1.65;white-space:pre-wrap}}h1,h2,h3,p,li,small,figcaption{{overflow-wrap:anywhere}}header{{border-bottom:3px solid #347461;padding-bottom:18px}}section{{padding:12px 0;border-bottom:1px solid #dedfd9}}figure{{margin:24px 0}}svg{{display:block;max-width:100%;height:auto}}small,figcaption{{color:#5b605b}}li{{margin:8px 0}}ul{{padding-left:22px}}.notice{{color:#865517;border-left:3px solid #c89342;padding-left:12px}}@media(max-width:480px){{main{{padding:18px 12px}}h1{{font-size:24px}}}}@media print{{section,figure{{break-inside:avoid}}}}
</style></head><body><main><header><h1>{text(report["title"])}</h1><p>{text(report["executive_summary"])}</p></header>
{"".join(sections)}<section><h2>Charts</h2>{"".join(figures) or '<p>No supported charts for this source.</p>'}</section>
<section><h2>Evidence register</h2><ul>{evidence}</ul></section><section><h2>Limitations</h2><ul>{limitations}</ul></section>
</main></body></html>'''


def prepare_message(session_id: str, message: dict[str, Any]) -> dict[str, Any]:
    payload, content = report_payload(message)
    if payload is None:
        if message.get("role") == "assistant" and "```inflak-report" in content and not (message.get("metadata") or {}).get("partial"):
            return {**message, "metadata": {**(message.get("metadata") or {}), "reportError": "HTML report unavailable: incomplete or invalid report data. Ask to regenerate the report."}}
        return message
    metadata = dict(message.get("metadata") or {})
    try:
        report = payload["generated_report"]
        rows, source = source_rows(session_id, payload.get("source_artifact_ref", ""))
        digest = hashlib.sha256(RENDER_VERSION.encode() + json.dumps(report, sort_keys=True).encode() + source).hexdigest()[:24]
        filename = f"analysis-report-{digest}.html"
        attachment = next((item for item in uploads_store.list_uploads(session_id) if item["name"] == filename), None)
        if attachment is None:
            attachment = uploads_store.save_generated_artifact(
                session_id=session_id, filename=filename,
                content=render_report(report, rows), mime="text/html",
            )
        metadata["report"] = {key: attachment[key] for key in ("fileId", "name", "mime", "size")}
        metadata["report"]["title"] = report["title"]
        metadata["report"]["summary"] = report["executive_summary"]
        return {**message, "content": content, "metadata": metadata}
    except (ValueError, TypeError, KeyError, OSError) as error:
        metadata["reportError"] = f"HTML report unavailable: {error}"
        return {**message, "metadata": metadata}