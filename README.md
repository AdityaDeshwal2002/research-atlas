# Research Atlas

**An evidence-grounded, generative workspace for scientific literature.**

Research Atlas is a Python-based hackathon prototype exploring how AI can turn a natural-language research question into an interactive, question-specific view of scientific publications. Its intended workflow searches PubMed and OpenAlex through Model Context Protocol (MCP) servers, preserves publication provenance, extracts findings from available research text, synthesizes comparable evidence, and renders a research workspace using FastMCP GenerativeUI and Prefab.

> **Project status:** The existing prototype has validated its development environment, a minimal Prefab render, an OpenAI-backed LiteLLM structured-output demo, and a PydanticAI research planner. **The full evidence-analysis and dynamically generated research UI workflow is planned, not yet verified by the supplied project records.** See [Current status](#current-status) below.

## Why this project?

Scientific literature searches can return hundreds or thousands of results. Researchers need more than a list of abstracts or an unsupported chatbot summary: they need ways to explore publication trends, identify recurring findings, inspect potentially differing evidence, understand coverage and limitations, and trace claims back to their sources.

Research Atlas aims to make the *interface itself* adapt to the question and the evidence available, without letting the UI-generating model invent scientific data.

## Intended research experience (Phase 1)

1. **Ask a question.** For example: “What does the literature say about early-onset colorectal cancer in adults under 50?”
2. **Plan a search.** PydanticAI creates a validated `ResearchPlan` containing the original question and provider-neutral search terms.
3. **Retrieve publications.** Deterministic Python orchestration queries **PubMed MCP** and **OpenAlex MCP** and retains tool responses and source identifiers.
4. **Normalize and deduplicate.** Create canonical paper records, preserve DOI/PMID/OpenAlex identifiers and provenance, and retain incomplete records for appropriate bibliometric use.
5. **Extract research findings.** Meta models produce structured, source-linked findings from available abstracts or other accessible text. A paper may yield zero or multiple findings. Missing information is not filled in by guesswork.
6. **Synthesize evidence hierarchically.** Group sufficiently comparable findings, preserve their paper/evidence references, and distinguish recurring results, potential conflicts, and non-comparable studies.
7. **Generate a research UI.** A compact `ResearchInsightPackage` supplies grounded statistics and evidence to **FastMCP GenerativeUI + Prefab**, which selects useful representations for the question.
8. **Inspect provenance and coverage.** Users can drill into source publications; the interface indicates which papers were retrieved and which were actually analyzed.

The project does **not** treat topic similarity as scientific agreement, nor does it treat an abstract-level finding as clinical advice or a validated systematic-review conclusion.

## Intended architecture

```text
Natural-language research question
                |
                v
        PydanticAI ResearchPlan
                |
       LiteLLM gateway -> Meta Model API
                |
                v
   Deterministic Python orchestration
        /                   \
 OpenAlex MCP             PubMed MCP
        \                   /
         Raw MCP source responses
                |
       Normalize + deduplicate
                |
          ResearchDataset
                |
   Structured, per-paper Meta extraction
                |
           EvidenceDataset
                |
    Hierarchical, source-linked synthesis
                |
            EvidenceGroups
                |
        ResearchInsightPackage
                |
        GenerativeUI + Prefab
                |
           Rendered MCP App

OpenTelemetry tracing spans planning, retrieval, analysis, and UI.
```

**Architectural principles:** MCP for both research-source integrations; deterministic processing for identifiers, statistics, and chart values; Pydantic validation for AI outputs; preservation of original source links; a separate compact analysis package for UI generation; and explicit processing/coverage status.

## Technology choices

| Area | Choice / status |
| --- | --- |
| Language | Python 3.13 (existing environment last validated on 3.13.5) |
| MCP server and app hosting | FastMCP, MCP Apps (`fastmcp dev apps` during prototype work) |
| Generative interface | FastMCP GenerativeUI + Prefab |
| Structured AI processing | PydanticAI + Pydantic |
| Model gateway | LiteLLM Proxy in a separate environment/process |
| Target hackathon models | Meta Model API (**integration pending live verification**) |
| Research sources | PubMed MCP and OpenAlex MCP (**planned, not yet integrated in supplied status**) |
| Bibliometrics / deduplication | LitStudy preferred for evaluation; compatibility and input conversion unverified |
| Observability | OpenTelemetry with a tracing backend (Langfuse provisionally preferred); planned |

The old M2/M3 demos used an **OpenAI upstream** model behind LiteLLM's `research-planner` alias. Moving that alias to Meta is a planned hackathon change, not an already completed integration.

## Current status

The following is the **last documented state from the original project files**; it is not a fresh audit of the live Git repository.

| Milestone | Last documented result |
| --- | --- |
| M0 — Repository bootstrap | Complete: Python environment, dependencies and development checks validated |
| M1 — Minimal Generative UI | Complete: FastMCP exposed provider tools and rendered **manually supplied** Prefab UI |
| M2 — Model gateway | Complete: PydanticAI structured output through LiteLLM to OpenAI |
| M3 — Research planner | Complete: validated `ResearchPlan` with 1–8 search terms; prior tests passed |
| New hackathon Phase 1 | **Not yet documented as implemented:** Meta provider, real paper retrieval, evidence processing, hierarchical synthesis, real-data generated UI, and end-to-end tracing |

**Important:** The M1 test established a UI-provider/rendering path, **not** automatic LLM-generated interface design. The documented planner generated search terms, **not** OpenAlex/PubMed-specific tool queries.

## Local development (historically validated setup)

The original project ran Research Atlas on native **Windows Python 3.13**, with **LiteLLM as a separate Windows process**; WSL was used for CLI work. The handoff reported a local LiteLLM endpoint at `127.0.0.1:4000`, an application `.venv`, and a separate `.litellm-venv`. Those paths are local environment conventions, not guaranteed in a new clone.

The repository's dependency manifests are `pyproject.toml`, `requirements.txt`, and `requirements-dev.txt`. Consult the current repository and `.env.example` for the actual dependency and configuration requirements; do not commit provider credentials or locally configured gateway files.

Once the appropriate environments and dependencies are configured, the previously used checks were:

```bash
ruff check .
pytest
```

The historical UI development command was:

```bash
fastmcp dev apps server.py
```

This command previews the **existing minimal provider**, not necessarily the new end-to-end research experience. The live LiteLLM service and model credentials must be configured separately for model-backed requests. There is not yet a verified, clone-to-demo setup procedure for the new Meta/MCP workflow; one should be documented after its integration has been tested.

## Phase roadmap

- **Phase 1 — Core hackathon experience:** Meta-backed research planning, MCP retrieval, provenance-preserving normalization/deduplication, multi-finding evidence extraction, hierarchical synthesis, question-adaptive Prefab interface, and traceability/observability.
- **Phase 2 — Analysis enhancements (only if needed):** Evaluate lexical/semantic ranking, topic clustering, and approaches such as TF-IDF, BM25, or BERTopic based on measured gaps.
- **Phase 3 — Interactive planning:** Ask clarifying questions and let researchers refine/approve search strategies.
- **Phase 4 — Literature screening:** Human-reviewed inclusion/exclusion decisions based on transparent criteria; evaluate existing screening tools as appropriate.

The ambition is to process collections on the order of **1,500–2,500 retrieved papers**, but retrieval volume is **not** a claim of having extracted and compared evidence from that many papers. Actual benchmarked counts, latency, and token costs must be reported as measured.

## Evidence integrity and limitations

- Source metadata and chart values must come from retrieved records and deterministic calculation, not invented LLM outputs.
- A paper can yield multiple findings, no qualifying findings, or an extraction error; these cases are not interchangeable.
- Source-linked quotations/passages should be checked against the material supplied for extraction.
- Conflicting statistical significance results alone do not prove contradictory science; comparability depends on population, design, exposure/intervention, and outcome.
- Abstracts can omit details required for reliable cross-study comparisons. Report uncertainty, missing abstracts, missing effects, and analysis coverage.
- This is an exploratory research prototype, **not medical advice, a clinical recommendation system, or a validated systematic review**.

## Observability

The intended pipeline carries a `run_id` through planning, MCP calls, normalization, extraction, synthesis, and UI generation. OpenTelemetry spans and a compatible LLM trace viewer should show model usage and latency, tool failures, retry counts, coverage, and rendering problems. Secrets and unredacted document/prompt contents must not be logged by default.

## Hackathon provenance and open source

Research Atlas began **before** the Meta Global AI Developer Hackathon. The pre-existing foundation included M0–M3: the development environment, minimal Prefab rendering experiment, LiteLLM/OpenAI structured-output demo, and the PydanticAI research planner. These components must be distinguished from features built during the hackathon in the submitted repository and demo. The event requires new hackathon work to be open source and calls for explicit disclosure of prior work.

The Git history and current working tree are authoritative for exact dates and feature attribution; this README must be updated when new functionality is actually implemented. The earlier handoff noted that some project documentation and `AGENTS.md` were gitignored: confirm what is publicly visible before submission, without publishing secrets.

## References

- [FastMCP](https://github.com/PrefectHQ/fastmcp)
- [Prefab](https://github.com/PrefectHQ/prefab)
- [MCP Apps](https://github.com/modelcontextprotocol/ext-apps)
- [PydanticAI](https://ai.pydantic.dev/)
- [LiteLLM](https://docs.litellm.ai/)
- [OpenAlex MCP candidate](https://github.com/oksure/openalex-research-mcp)
- [PubMed MCP candidate](https://github.com/JackKuo666/PubMed-MCP-Server)
- [LitStudy](https://pypi.org/project/litstudy/)

For contribution conventions and approved implementation boundaries, see `AGENTS.md` **if it is included in your checkout**. Further design details may live in private or in-progress project planning documents and should not be assumed to be present in a public clone.
