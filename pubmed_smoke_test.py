"""Inspect and smoke-test the sibling PubMed MCP server over stdio."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

PROJECT_ROOT = Path(__file__).resolve().parent
PUBMED_ROOT = PROJECT_ROOT.parent / "PubMed-MCP-Server"
PUBMED_SERVER = PUBMED_ROOT / "pubmed_server.py"
if sys.platform == "win32":
    PUBMED_PYTHON = PUBMED_ROOT / ".venv" / "Scripts" / "python.exe"
else:
    PUBMED_PYTHON = PUBMED_ROOT / ".venv" / "bin" / "python"
SEARCH_KEYWORDS = "artificial intelligence pancreatic cancer early detection"


def unwrap(value: Any) -> Any:
    """Unwrap FastMCP/Pydantic result wrappers into plain JSON data."""

    if hasattr(value, "result"):
        return unwrap(value.result)
    if hasattr(value, "root"):
        return unwrap(value.root)
    if hasattr(value, "model_dump"):
        try:
            return unwrap(value.model_dump())
        except Exception:
            pass
    if isinstance(value, dict) and set(value.keys()) == {"result"}:
        return unwrap(value["result"])
    if isinstance(value, (list, tuple)):
        return [unwrap(item) for item in value]
    return value


def extract_payload(result: Any) -> Any:
    """Return structured data from a FastMCP tool result."""

    if result.is_error:
        raise RuntimeError("PubMed MCP reported a tool error.")

    if result.data is not None:
        return unwrap(result.data)
    if result.structured_content is not None:
        return unwrap(result.structured_content)

    texts = [block.text for block in result.content if hasattr(block, "text")]
    if not texts:
        raise RuntimeError("PubMed MCP returned no readable content.")
    try:
        return unwrap(json.loads(texts[0]))
    except json.JSONDecodeError:
        return texts[0]


async def main() -> None:
    """List PubMed tools and run one small keyword search plus metadata check."""

    if not PUBMED_SERVER.is_file():
        raise FileNotFoundError(f"PubMed server not found: {PUBMED_SERVER}.")
    if not PUBMED_PYTHON.is_file():
        raise FileNotFoundError(
            f"PubMed venv Python not found: {PUBMED_PYTHON}. "
            "Create .venv in PubMed-MCP-Server and install requirements.txt."
        )

    transport = PythonStdioTransport(
        script_path=PUBMED_SERVER,
        cwd=str(PUBMED_ROOT),
        python_cmd=str(PUBMED_PYTHON),
        keep_alive=False,
    )

    async with Client(transport, mode="legacy") as client:
        tools = await client.list_tools()
        tool_by_name = {tool.name: tool for tool in tools}
        print(f"Discovered {len(tools)} PubMed MCP tools.")

        for name in ("search_pubmed_key_words", "get_pubmed_article_metadata"):
            tool = tool_by_name.get(name)
            if tool is None:
                raise RuntimeError(f"Required PubMed MCP tool is missing: {name}")
            print(f"\n{name} input schema:")
            print(json.dumps(tool.input_schema, indent=2))

        search_result = await client.call_tool(
            "search_pubmed_key_words",
            {"key_words": SEARCH_KEYWORDS, "num_results": 3},
        )
        articles = extract_payload(search_result)
        if isinstance(articles, dict) and "error" in articles:
            raise RuntimeError(f"PubMed search error: {articles['error']}")
        if not isinstance(articles, list):
            raise RuntimeError(f"Unexpected PubMed search shape: {type(articles)}")
        print(f"\nSearch returned {len(articles)} articles.")

        for index, article in enumerate(articles, start=1):
            abstract = article.get("Abstract", "")
            print(
                f"{index}. title={article.get('Title')!r}; PMID={article.get('PMID')!r}; "
                f"journal={article.get('Journal')!r}; date={article.get('Publication Date')!r}; "
                f"abstract_chars={len(abstract) if abstract else 0}"
            )

        if not articles:
            raise RuntimeError("PubMed search completed but returned no articles.")

        first_pmid = articles[0].get("PMID")
        if not first_pmid:
            raise RuntimeError("First PubMed result did not include a PMID.")

        metadata_result = await client.call_tool(
            "get_pubmed_article_metadata", {"pmid": first_pmid}
        )
        metadata = extract_payload(metadata_result)
        print("\nget_pubmed_article_metadata for first result:")
        print(json.dumps(metadata, indent=2)[:2000])


if __name__ == "__main__":
    asyncio.run(main())
