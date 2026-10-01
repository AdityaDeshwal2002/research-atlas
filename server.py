"""Research Atlas MCP server for the M1 Generative UI prototype."""

from fastmcp import FastMCP
from fastmcp.apps.generative import GenerativeUI

mcp = FastMCP("Research Atlas")
mcp.add_provider(GenerativeUI())
