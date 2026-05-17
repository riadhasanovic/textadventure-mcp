"""
MCP Server - Tools für Jacob Miller Textadventure
"""
from mcp.server.fastmcp import FastMCP
import logging
import sys

# WICHTIG: Alle globalen Variablen importieren
from world import WORLD, current_room, inventory

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Jacob Miller")

@mcp.tool(
    name="look",
    title="Beschreibe den aktuellen Ort",
    description="Zeigt den aktuellen Ort und alle erreichbaren Ziele."
)
def look() -> str:
    room = WORLD[current_room]
    
    output = [f"**{room.name}**", room.description, ""]

    if room.items:
        output.append(f"Gegenstände hier: {', '.join(room.items)}")
        output.append("")

    if room.exits:
        output.append("Von hier aus kannst du folgende Orte erreichen:")
        for richtung, ziel in room.exits.items():
            ziel_name = WORLD[ziel].name
            output.append(f"  • {richtung.capitalize():<12} → {ziel_name}")

    return "\n".join(output)


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
    else:
        return f"Du kannst nicht nach {direction} gehen."


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
def inventory_tool() -> str:
    if inventory:
        return f"In deinem Inventar: {', '.join(inventory)}"
    return "Dein Inventar ist leer."


@mcp.tool(
    name="use",
    title="Benutze einen Gegenstand",
    description="Benutzt einen Gegenstand am aktuellen Ort."
)
def use(item: str) -> str:
    if item not in inventory:
        return f"Du hast '{item}' nicht im Inventar."

    if current_room == "parkplatz_baseballstadion" and item in ["reifen_reparaturset", "wagenheber", "radkreuz"]:
        return "✅ Du reparierst den Reifen am Auto von Coach Ferguson."

    if current_room == "stadtbuecherei" and item == "warhammer_brettspiel":
        return "✅ Du stellst das Brettspiel auf den Tisch."

    if current_room == "stadtbuecherei" and item == "foto_dnd_freunde":
        return "✅ Du betrachtest das alte Foto."

    return f"Du weißt nicht, was du mit '{item}' an diesem Ort machen kannst."


if __name__ == "__main__":
    logger.info("🚀 MCP Server gestartet")
    mcp.run(transport="stdio")

@mcp.tool(
    name="in_hand",
    title="Nimm einen Gegenstand in die Hand",
    description="Nimmt einen Gegenstand aus dem Inventar in die Hand (bereithalten)."
)
def in_hand(item: str) -> str:
    if item not in inventory:
        return f"Du hast '{item}' nicht im Inventar."

    # Hier kannst du später spezielle Effekte einbauen
    return f"Du nimmst '{item}' in die Hand. Du hältst es jetzt bereit."