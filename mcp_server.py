"""
MCP Server - Tools für Jacob Miller Textadventure
"""
from mcp.server.fastmcp import FastMCP
import logging
import sys
from world import WORLD, current_room, inventory

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Jacob Miller")

@mcp.tool(
    name="look",
    title="Beschreibe den aktuellen Ort",
    description="Gibt eine detaillierte Beschreibung des aktuellen Ortes."
)
def look() -> str:
    room = WORLD[current_room]
    desc = f"**{room.name}**\n{room.description}\n\n"
    if room.items:
        desc += f"Gegenstände hier: {', '.join(room.items)}\n"
    desc += f"Ausgänge: {', '.join(room.exits.keys())}"
    return desc

@mcp.tool(
    name="move",
    title="Bewege dich in eine Richtung",
    description="Mögliche Richtungen: norden, süden, osten, westen"
)
def move(direction: str) -> str:
    global current_room
    room = WORLD[current_room]
    if direction in room.exits:
        current_room = room.exits[direction]
        return look()
    return "Dorthin führt kein Weg."

@mcp.tool(
    name="take",
    title="Nimm einen Gegenstand auf",
    description="Nimmt einen Gegenstand auf, falls vorhanden."
)
def take(item: str) -> str:
    global inventory
    room = WORLD[current_room]
    if item in room.items:
        room.items.remove(item)
        inventory.append(item)
        return f"Du hast '{item}' aufgenommen."
    return f"'{item}' gibt es hier nicht."

@mcp.tool(
    name="inventory",
    title="Zeige dein Inventar",
    description="Zeigt alle gesammelten Gegenstände."
)
def inventory() -> str:
    if inventory:
        return f"In deinem Inventar: {', '.join(inventory)}"
    return "Dein Inventar ist leer."

if __name__ == "__main__":
    logger.info("🚀 MCP Server gestartet")
    mcp.run(transport="stdio")