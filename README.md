# Inflak Demo

Inflak Demo includes the Copilot SDK host, FastAPI backend, web frontend, CLI,
and 17 registered Inflak plugins.

## Start

```bash
source .venv/bin/activate
./start
```

Open http://127.0.0.1:8002 .
Repeated starts reuse this project's existing server. The default model is
`gpt-5.5`; the default agent working directory is this project.

```bash
./start --cli
```

GitHub CLI must be installed and authenticated with a Copilot-enabled account.
Activate your Python 3.11+ environment before starting. The examples use `.venv`;
replace it with your environment's path if needed.

## Installation

Use Python 3.11+, Node.js 18+ with npm, GitHub CLI, and zsh:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm ci
gh auth login
./start
```

Image generation requires a configured image provider. Use environment variables
or copy `backend/services/local_config.example.py` to
`backend/services/local_config.py` and configure it locally. The local config is
ignored by Git; do not include credentials when sharing the project.

## Contents

- `backend/`: session management, tools, artifact services, plugin authoring.
- `backend/services/plugin_tools/shared/`: Host tools and execution guards shared by all plugins.
- `backend/services/plugin_tools/{image,collage,reporting,author}/`: task-specific plugin tool implementations grouped by domain.
- `frontend/`: chat, widgets, artifact canvas, and authoring interfaces.
- `plugins/`: active plugins, skills, registries, authoring contracts.
- `start`, `chat_cli.py`: web and terminal entry points.
- `node_modules/`: JavaScript dependencies installed by `npm ci`, including Vega rendering.
- `data/`: created on demand for new sessions, uploads, and generated artifacts.
