# Request Lifecycle

This document describes the eventual Research Atlas request lifecycle.

Not every stage exists in the current implementation.

## Current M3 lifecycle

```text
Research question
   ↓
PydanticAI Research Planner
   ↓
LiteLLM Proxy
   ↓
OpenAI
   ↓
Validated ResearchPlan
```

The research-source retrieval stages are not implemented yet. OpenAlex and
PubMed searches are planned for later milestones.

## Current M1 UI preview lifecycle

```text
Developer
   ↓
fastmcp dev apps
   ↓
Research Atlas FastMCP Server
   ↓
GenerativeUI
   ↓
Prefab
   ↓
Rendered MCP App
