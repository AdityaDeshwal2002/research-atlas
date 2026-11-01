# Research Atlas — Project Handoff

## Why this document exists

The project owner is considering a change in approach. Treat this document and
the existing project docs as **context and past decisions, not fixed
requirements**. Discuss the new goal and tradeoffs with the owner before changing
the architecture or implementing it.

The owner is a software developer using this project both to build something
useful and to learn programming, system design, architecture, MCP, PydanticAI,
and Generative UI. They prefer a conversation about the problem, options,
recommendation, and tradeoffs **before substantive code changes**. Explain
relevant concepts clearly as work proceeds.

## Original project goal

Research Atlas is a learning-focused prototype for exploring scientific
literature from a natural-language question, such as:

> Show me research on AI for early pancreatic cancer detection.

The original proposed end-to-end flow was:

1. Produce a structured `ResearchPlan`.
2. Search OpenAlex and PubMed through MCP.
3. Normalize the returned papers.
4. Deduplicate papers while preserving provenance and identifiers.
5. Build a canonical `ResearchDataset`.
6. Pass that dataset to Generative UI.
7. Render a generated Prefab interface through FastMCP's development app host.

This **full flow has not been built**. The project was intended as a small
prototype, not a production service.

## Original architecture

```text
Research question
    ↓
PydanticAI planner
    ↓
LiteLLM Proxy → OpenAI model
    ↓
ResearchPlan
    ↓
Deterministic Python orchestration
    ├── OpenAlex MCP
    └── PubMed MCP
    ↓
Normalization → deduplication → ResearchDataset
    ↓
FastMCP GenerativeUI → Prefab → rendered MCP App
```

The model creates a structured plan. Deterministic Python was intended to choose
and call research-source tools and process their results. LiteLLM is an
externally running model gateway, **not** a provider of models or shared model
credits.

## What works today

### M0 — Environment

Research Atlas uses Python 3.13; the validated Windows installation was Python
3.13.5. Project dependencies include `fastmcp[apps]`, Pydantic, Pydantic
Settings, and `pydantic-ai-slim[openai]`. Development tools include pytest,
pytest-asyncio, and Ruff.

### M1 — Minimal Generative UI

`server.py` creates a FastMCP server and registers `GenerativeUI()` with its
default tools. A test checks that `generate_prefab_ui` and
`search_prefab_components` are exposed. A small Prefab UI was rendered using
`fastmcp dev apps server.py`.

**Important distinction:** Prefab code was supplied manually for this test. M1
proved the provider/rendering path, not that an LLM can design the UI.

### M2 — Model gateway

`gateway_demo.py` defines a small structured output, `DemoResult(answer: str)`.
PydanticAI connected through a local LiteLLM Proxy to OpenAI, and a live call
returned a validated response:

```json
{"answer": "Confirmed—the model gateway request succeeded."}
```

LiteLLM 1.103.2 was installed separately in a Windows virtual environment,
`.litellm-venv/`. It is **not** an application runtime dependency. The local
LiteLLM configuration maps the alias `research-planner` to
`openai/gpt-6-luna`. The gateway runs on Windows at `127.0.0.1:4000`; Research
Atlas uses its own Windows `.venv`. WSL is preferred for CLI work on the files,
not as the application runtime.

An initial live call failed because an OpenAI API key had expired; after the key
was replaced, the call succeeded. Never ask for or copy actual key values into a
prompt or public file.

### M3 — Research planner

`research_plan.py` defines `ResearchPlan` with:

- `original_question: str`
- `search_terms: list[str]` — 1 to 8 provider-neutral search terms

It rejects blank values, trims whitespace, and removes case-insensitive
duplicate terms.

`planner.py` asks PydanticAI to return that structured plan. Python supplies the
original user question in the returned object rather than trusting the model to
reproduce it. `model_gateway.py` holds the shared LiteLLM connection setup used
by the M2 demo and planner.

A live planning request succeeded for:

> Show me research on AI for early pancreatic cancer detection.

It produced the original question plus five search terms. At the last reported
validation, `ruff check .`, `pytest` (**8 tests**), and `pip check` passed.
Automated planner tests use a simulated model and make no paid API calls.

**Current limitation:** `search_terms` are generated text, not yet
source-specific OpenAlex or PubMed queries. No paper retrieval is implemented.

## Where work paused

The original implementation plan calls the next milestone **M4 — OpenAlex MCP**:
connect Research Atlas as an MCP client, call one search tool, and preserve the
result.

A candidate MCP server is `oksure/openalex-research-mcp`. It can run via `npx`
and exposes `search_works`; Windows Node and npx were available at the last
check. FastMCP can connect to an MCP server over STDIO.

**Unresolved design question:** That candidate server summarizes search results.
Preserving its untouched *MCP tool result* is not the same thing as preserving
the original, unmodified *OpenAlex REST API payload*. The owner had not yet
chosen which meaning of “raw response” they need. **M4 has not been
implemented.**

The owner has since said the project direction may change, so do not assume M4
remains the right next step.

## Original later milestones (plans, not implemented features)

- M5: PubMed MCP and concurrent source searches.
- M6: canonical paper model, provenance, DOI-first deduplication.
- M7: canonical dataset and deterministic statistics.
- M8: generate a research UI using real dataset contents.
- M9: telemetry.
- M10: end-to-end prototype.

These are a record of the prior direction and can be revisited.

## Files and repository state

Key code files:

- `server.py` — FastMCP server and Generative UI provider.
- `gateway_demo.py` — M2 structured-output demo.
- `model_gateway.py` — shared LiteLLM model client and settings.
- `research_plan.py` — M3 plan data contract.
- `planner.py` — M3 planning agent and CLI.
- `tests/` — provider, demo, schema, and planner tests.
- `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` — project
  dependencies and tooling.
- `README.md` — public-facing setup and status.

Private/local files under `.gitignore` include `docs/`, `AGENTS.md`,
`CodingAgentSession.md`, `.env`, both virtual environments, `scripts/`,
`litellm_config.yaml`, and `requirements-litellm.txt`. The `.env.example` file is
public and contains placeholder values only.

The public GitHub repository exists. At the last Git check, `main` tracked
`origin/main`, and the latest commit was `ce37859 PydanticAI gateway demo`.
**The M3 code and tests were still uncommitted/untracked locally.** There were
also local modifications to `README.md` and `gateway_demo.py`, plus apparent
line-ending-only modifications in `pyproject.toml`, `requirements.txt`, and
`requirements-dev.txt`. Inspect the current Git status before editing,
committing, or pushing. Do not discard local work.

Private planning docs currently mark M0–M3 complete and M4 as next, based on the
**old approach**. The high-level architecture diagram also depicts future
components that do not yet exist in code.

## Previous project constraints and preferences

- Python 3.13; keep v1 intentionally small.
- Previously selected academic sources: OpenAlex and PubMed only.
- Prefer deterministic Python orchestration over letting an LLM call every MCP
  tool directly.
- Generative UI was the primary experiment; FastMCP + Prefab were selected for
  it.
- PydanticAI was selected for structured planning.
- LiteLLM and vLLM are external services, not Research Atlas runtime
  dependencies.
- Preserve actual publication provenance and identifiers; do not fabricate
  metadata obtainable from the sources.
- Discuss any change in scope and update private decisions/docs accordingly.
- After code changes, run `ruff check .` and `pytest`; run `pip check` when
  dependencies change. Update status docs after completing a milestone.

**These are previous decisions, not instructions to reject the owner's
forthcoming change of plans.**

## How to resume the conversation

First ask the owner to describe the new hackathon/project direction. Compare it
with what already works and identify what can be reused, what should change, and
what can be dropped. Explain options and tradeoffs before implementation. Do not
treat unimplemented roadmap stages as completed features, and do not expose
local credentials or private docs in the public repository.
