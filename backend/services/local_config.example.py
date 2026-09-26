"""Template config for image tools (safe to commit).

Copy this file to local_config.py for local-only usage.
Do not commit real secrets.

Resolution order for each value: environment variable > local_config.py > built-in default.
"""

# Keep empty or use a placeholder. Put real secrets only in local_config.py.
AZURE_OPENAI_API_KEY = "<YOUR_AZURE_OPENAI_API_KEY>"

# Optional model-related overrides.
AZURE_OPENAI_ENDPOINT = "<YOUR_AZURE_OPENAI_ENDPOINT>"
AZURE_OPENAI_IMAGE_DEPLOYMENT = "gpt-image-1.5"
AZURE_OPENAI_AUTH = "azure_cli"
