# Inflak-demo

Standalone runtime extracted from the research workspace. Includes the Copilot
SDK host, FastAPI backend, web frontend, CLI, and 17 registered Inflak plugins.

## Start on this machine

```bash
conda activate opendeepresearch
./start
```

Open http://127.0.0.1:8002 . The original research workspace uses port 8001.
Repeated starts reuse this project's existing server. The default model is
`gpt-5.5`; the default agent working directory is this project.

```bash
./start --cli
```

GitHub CLI must be installed and authenticated with a Copilot-enabled account.
The Python environment is external to this folder. JavaScript dependencies
are included locally; no link to the original project is required.

## Install on another machine

Use Python 3.11+, Node.js 18+ with npm, GitHub CLI, and zsh:

```bash
git clone https://github.com/Inflak-orchestration/Inflak-demo.git
cd Inflak-demo
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm ci
gh auth login
./start
```

Image generation requires your own configured image provider. Copy
`backend/services/local_config.example.py` to
`backend/services/local_config.py` and configure it locally, or use environment
variables. Copilot authentication and image-provider (including ImagePAI)
credentials are not distributed with this repository.

## Contents

- `backend/`: session management, tools, artifact services, plugin authoring.
- `backend/services/plugin_tools/shared/`: Host tools and execution guards shared by all plugins.
- `backend/services/plugin_tools/{image,collage,reporting,author}/`: task-specific plugin tool implementations grouped by domain.
- `frontend/`: chat, widgets, artifact canvas, and authoring interfaces.
- `plugins/`: active plugins, skills, registries, authoring contracts.
- `start`, `chat_cli.py`: web and terminal entry points.
- `node_modules/`: installed JavaScript dependencies, including Vega rendering.
- `data/`: created on demand for new sessions, uploads, and generated artifacts.

Plugin-local `tests/scenarios.json` files are retained because publication and
runtime acceptance use them. Backend unit tests, research evaluation, historical
data, logs, examples, plugin archives, Git history, paper/video assets, and the
external gallery interface are not included. New-session case recording remains
available for research traces.

The private `backend/services/local_config.py`, environment files, authentication
caches, logs, and runtime data are ignored by Git. Never commit credentials.
Use your own Copilot-enabled account with `gh auth login`; GitHub authentication
remains in your machine's login store. Remove private configuration and runtime
data before sharing the folder outside Git.