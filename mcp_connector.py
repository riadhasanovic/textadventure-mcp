"""
MCP Connector - Verbindung zum MCP Server und Tool-Ausführung
"""
import sys
import os
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)

SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")


@dataclass
class ToolResult:
    """Ergebnis eines Tool-Aufrufs"""
    success: bool
    output: str
    error: str | None = None


class MCPConnector:
    """Verwaltet die Verbindung zum MCP Server."""

    def __init__(self):
        self.session = None
        self.tools_description: str = ""
        self._tools_list = []

    @asynccontextmanager
    async def connect(self):
        """
        Kontextmanager für die MCP-Verbindung.
        """
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[SERVER_SCRIPT],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()

                # Tools laden
                tools = await session.list_tools()
                self._tools_list = tools.tools
                self.tools_description = "\n".join(
                    f"- {t.name}: {t.description}" for t in self._tools_list
                )

                logger.info(f"MCP Server verbunden. {len(self._tools_list)} Tool(s) verfügbar.")

                try:
                    yield self
                finally:
                    self.session = None

    async def call_tool(self, tool_name: str, arguments: dict) -> ToolResult:
        """Ruft ein Tool auf dem MCP Server auf."""
        if not self.session:
            return ToolResult(success=False, output="", error="Keine Verbindung zum MCP Server")

        try:
            logger.debug(f"Tool aufrufen: {tool_name}({arguments})")
            result = await self.session.call_tool(tool_name, arguments=arguments)

            if result.isError:
                error_msg = str(result.content) if result.content else "Unbekannter Fehler"
                return ToolResult(success=False, output="", error=error_msg)

            output = result.content[0].text if result.content else ""
            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Fehler beim Tool-Aufruf: {e}")
            return ToolResult(success=False, output="", error=str(e))

    def get_tools_description(self) -> str:
        """Gibt die Beschreibung aller verfügbaren Tools zurück."""
        return self.tools_description