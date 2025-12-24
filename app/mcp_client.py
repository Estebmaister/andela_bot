import asyncio
import logging
from typing import Any, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from app.config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to the company's MCP server via Streamable HTTP."""

    def __init__(self, server_url: str):
        self.server_url = server_url

    @asynccontextmanager
    async def get_session(self):
        """Get an active MCP session."""
        async with streamablehttp_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from the MCP server."""
        try:
            async with self.get_session() as session:
                response = await session.list_tools()
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    for tool in response.tools
                ]
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
            return []

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Call a tool on the MCP server."""
        try:
            async with self.get_session() as session:
                result = await session.call_tool(name, arguments)
                # Extract text content from result
                if result.content:
                    content = result.content[0]
                    return content.text if hasattr(content, "text") else str(content)
                return "No content returned"
        except Exception as e:
            logger.error(f"Tool call failed: {name}({arguments}): {e}")
            return f"Error: {str(e)}"

    async def health_check(self) -> bool:
        """Check if MCP server is accessible."""
        try:
            async with self.get_session() as session:
                await session.initialize()
                return True
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return False


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient(server_url=settings.MCP_SERVER_URL)
    return _mcp_client
