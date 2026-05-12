from fastmcp import FastMCP
from world import WORLD, current_room, inventory, collected_notes
from typing import Literal

mcp = FastMCP("SlenderMan")

@mcp.tool
def look() -> str:
    """Beschreibt den aktuellen Ort sehr atmosphärisch."""
    room = WORLD[current_room]
    desc = f"**{room.name}**\n{room.description}\n\n"
    
    if room.items:
        desc += f"Du siehst hier: {', '.join(room.items)}\n"
    
    desc += f"Ausgänge: {', '.join(room.exits.keys())}"
    
    if collected_notes > 0:
        desc += f"\n\nDu hast bereits {collected_notes}/8 Zettel gesammelt..."
    
    return desc

@mcp.tool
def move(direction: Literal["norden", "sueden", "osten", "westen"]) -> str:
    """Bewege dich in eine Richtung."""
    global current_room
    room = WORLD[current_room]
    if direction in room.exits:
        current_room = room.exits[direction]
        return look()
    else:
        return "Du kannst nicht in diese Richtung gehen. Der Wald ist zu dicht."

@mcp.tool
def take(item: str) -> str:
    """Nimm einen Gegenstand (Zettel) auf."""
    global collected_notes
    room = WORLD[current_room]
    if item in room.items:
        room.items.remove(item)
        inventory.append(item)
        collected_notes += 1
        return f"Du hast **{item}** aufgenommen. Deine Hände zittern..."
    return "Das gibt es hier nicht."

@mcp.tool
def inventory() -> str:
    """Zeigt dein Inventar."""
    if inventory:
        return f"Gesammelte Zettel: {', '.join(inventory)}\nInsgesamt: {collected_notes}/8"
    return "Du hast noch keine Zettel."

if __name__ == "__main__":
    print("🌲 Slender Man - The Forest | MCP Server gestartet...")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
