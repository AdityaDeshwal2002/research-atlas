"""Inspect and smoke-test the sibling OpenAlex MCP server over stdio."""

import asyncio
import json
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import NodeStdioTransport

PROJECT_ROOT = Path(__file__).resolve().parent
OPENALEX_ROOT = PROJECT_ROOT.parent / "openalex-research-mcp"
OPENALEX_SERVER = OPENALEX_ROOT / "build" / "index.js"
SEARCH_QUERY = "artificial intelligence pancreatic cancer early detection"


def parse_json_tool_result(result: Any) -> dict[str, Any]:
    """Parse the JSON text returned by an OpenAlex MCP tool."""

    if result.is_error:
        raise RuntimeError("OpenAlex MCP reported a tool error.")

    for block in result.content:
        if hasattr(block, "text"):
            value = json.loads(block.text)
            if isinstance(value, dict):
                return value

    raise RuntimeError("OpenAlex MCP returned no JSON object in its text content.")


async def main() -> None:
    """List OpenAlex tools, search three works, and inspect one full record."""

    if not OPENALEX_SERVER.is_file():
        raise FileNotFoundError(
            f"Built OpenAlex server not found: {OPENALEX_SERVER}. "
            'Run "npm ci" and "npm run build" in the openalex-research-mcp folder.'
        )

    transport = NodeStdioTransport(
        script_path=OPENALEX_SERVER,
        cwd=str(OPENALEX_ROOT),
        keep_alive=False,
    )

    async with Client(transport) as client:
        tools = await client.list_tools()
        tool_by_name = {tool.name: tool for tool in tools}
        print(f"Discovered {len(tools)} OpenAlex MCP tools.")

        for name in ("search_works", "get_work"):
            tool = tool_by_name.get(name)
            if tool is None:
                raise RuntimeError(f"Required OpenAlex MCP tool is missing: {name}")
            print(f"\n{name} input schema:")
            print(json.dumps(tool.input_schema, indent=2))

        search_result = await client.call_tool(
            "search_works",
            {"query": SEARCH_QUERY, "per_page": 3},
        )
        search_data = parse_json_tool_result(search_result)
        works = search_data.get("results", [])
        print(f"\nSearch returned {len(works)} works.")

        for index, work in enumerate(works, start=1):
            abstract = work.get("abstract")
            print(
                f"{index}. title={work.get('title')!r}; id={work.get('id')!r}; "
                f"doi={work.get('doi')!r}; year={work.get('publication_year')!r}; "
                f"abstract_chars={len(abstract) if abstract else 0}"
            )

        if not works:
            raise RuntimeError("OpenAlex search completed but returned no works.")

        first_id = works[0].get("id")
        if not first_id:
            raise RuntimeError("First OpenAlex result did not include a work ID.")

        detail_result = await client.call_tool("get_work", {"id": first_id})
        detail = parse_json_tool_result(detail_result)
        full_abstract = detail.get("abstract")
        search_abstract = works[0].get("abstract")
        print("\nget_work detail for first result:")
        print(f"title={detail.get('title')!r}")
        print(f"id={detail.get('id')!r}; doi={detail.get('doi')!r}")
        print(f"abstract_chars={len(full_abstract) if full_abstract else 0}")
        print(f"search_abstract_chars={len(search_abstract) if search_abstract else 0}")


if __name__ == "__main__":
    asyncio.run(main())
