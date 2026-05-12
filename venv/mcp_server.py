from fastmcp import FastMCP
from world import WORLD, current_room, inventory
from typing import Literal

mcp = FastMCP("TextAdventure")

@mcp.tool
def look() -> str:
    """Beschreibt den aktuellen Raum inklusive Gegenstände und Ausgänge."""
    room = WORLD[current_room]
    desc = f"**{room.name}**\n{room.description}\n\n"
    if room.items:
        desc += f"Gegenstände hier: {', '.join(room.items)}\n"
    desc += f"Ausgänge: {', '.join(room.exits.keys())}"
    return desc

@mcp.tool
def move(direction: Literal["norden", "sueden", "osten", "westen"]) -> str:
    """Bewegt den Spieler in die angegebene Richtung."""
    global current_room
    room = WORLD[current_room]
    if direction in room.exits:
        current_room = room.exits[direction]
        return look()  # direkt den neuen Raum beschreiben
    else:
        return "Dorthin gibt es keinen Weg!"

@mcp.tool
def take(item: str) -> str:
    """Nimmt einen Gegenstand auf, falls vorhanden."""
    global inventory
    room = WORLD[current_room]
    if item in room.items:
        room.items.remove(item)
        inventory.append(item)
        return f"Du hast '{item}' aufgenommen."
    return f"Das gibt es hier nicht."

@mcp.tool
def inventory() -> str:
    """Zeigt dein aktuelles Inventar."""
    if inventory:
        return f"In deinem Inventar: {', '.join(inventory)}"
    return "Dein Inventar ist leer."

if __name__ == "__main__":
    print("🚀 MCP TextAdventure Server gestartet...")
    mcp.run(transport="http", port=8000)   # HTTP für einfache Verbindung