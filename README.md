# Research Atlas

Research Atlas is an experimental scientific-literature exploration project built to study MCP composition and Generative UI.

The prototype combines:

- FastMCP
- MCP Apps
- Prefab
- PydanticAI
- OpenAlex MCP
- PubMed MCP
- LiteLLM / vLLM

## Current Status

M0 and M1, Minimal Generative UI, are complete. M2 is in progress: the project
is adding a PydanticAI call through a local LiteLLM gateway to OpenAI.

## Run

The initial server registers FastMCP's Generative UI provider. To preview it,
run:

```bash
fastmcp dev apps server.py
```

In the development picker, select `generate_prefab_ui` and submit Prefab Python
code. For example:

```python
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text

with PrefabApp() as app:
    with Column(gap=4, css_class="p-6"):
        Heading("Research Atlas")
        Text("M1 UI rendering check")
        Text("Research search is not connected yet.")
```

This manually supplied code checks that the provider can render a Prefab UI. It
does not test LLM-generated code.

## Development

Install dependencies in a Python 3.13 environment:

```bash
pip install -r requirements-dev.txt
```

Run checks:

```bash
ruff check .
pytest
pip check
```

## M2 — Model Gateway Demo

The M2 demo sends a PydanticAI request through an OpenAI-compatible LiteLLM
Proxy and validates the structured result. To run it live, configure a local
LiteLLM Proxy with the model alias `research-planner` and make it available at
`http://localhost:4000/v1`. Supply `LITELLM_MASTER_KEY` to the demo environment;
keep provider credentials in the gateway environment. `.env.example` lists the
expected local variable names. Never commit real credentials.

Run the demo using the Research Atlas environment:

```powershell
.\.venv\Scripts\python.exe gateway_demo.py
```

The automated tests use a simulated model and do not make API requests. A live
gateway call may incur token-based provider charges.
