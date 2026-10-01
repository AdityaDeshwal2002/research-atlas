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

M0 and M1, Minimal Generative UI, are complete. The current prototype exposes a
minimal FastMCP server with FastMCP's Generative UI provider.

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
