import pytest
from fastmcp import Client

from server import mcp


@pytest.mark.asyncio
async def test_generative_ui_tools_are_registered() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

    tool_names = {tool.name for tool in tools}
    assert "generate_prefab_ui" in tool_names
    assert "search_prefab_components" in tool_names
