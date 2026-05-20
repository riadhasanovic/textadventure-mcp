"""
MCP Server - Tools für Jacob Miller Textadventure
"""
from mcp.server.fastmcp import FastMCP
import logging
import sys
import world

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Jacob Miller")

# Tracks which of the three moral tasks Jacob has completed.
completed_tasks: set[str] = set()
# Tracks which repair tools have been used at the parking lot.
used_repair_tools: set[str] = set()

REPAIR_TOOLS = {"wagenheber", "reifen_reparaturset", "radkreuz"}
REQUIRED_TASKS = {"car_fixed", "friends_reconciled", "grandpa_forgiven"}


@mcp.tool(
    name="look",
    title="Beschreibe den aktuellen Ort",
    description="Zeigt den aktuellen Ort und alle erreichbaren Ziele."
)
def look() -> str:
    room = world.WORLD[world.current_room]

    if world.current_room == "lovers_leap":
        if completed_tasks >= REQUIRED_TASKS:
            return (
                f"**{room.name}**\n"
                f"{room.description}\n\n"
                "Die Krähen kreisen langsam über dir — und verschwinden dann lautlos in den Wolken.\n"
                "Der Nebel lichtet sich. Jacob hat sich seinen Fehlern gestellt.\n"
                "GAME_OVER_GOOD"
            )
        else:
            task_names = {
                "car_fixed": "Coach Fergusons Auto reparieren",
                "friends_reconciled": "D&D-Freunde versöhnen",
                "grandpa_forgiven": "Opa Geralds Erinnerungen ehren",
            }
            missing = [task_names[t] for t in REQUIRED_TASKS - completed_tasks]
            return (
                f"**{room.name}**\n"
                f"{room.description}\n\n"
                "Die Krähen kreischen. Du spürst: Die Zeit ist noch nicht reif.\n"
                f"Ungelöst: {', '.join(missing)}.\n"
                "GAME_OVER_BAD"
            )

    output = [f"**{room.name}**", room.description, ""]

    if room.items:
        output.append(f"Gegenstände hier: {', '.join(room.items)}")
        output.append("")

    if room.exits:
        output.append("Von hier aus kannst du folgende Orte erreichen:")
        for richtung, ziel in room.exits.items():
            ziel_name = world.WORLD[ziel].name
            output.append(f"  • {richtung.capitalize():<12} → {ziel_name}")

    return "\n".join(output)


@mcp.tool(
    name="move",
    title="Bewege dich in eine Richtung",
    description="Mögliche Richtungen: norden, süden, osten, westen"
)
def move(direction: str) -> str:
    room = world.WORLD[world.current_room]
    if direction in room.exits:
        world.current_room = room.exits[direction]
        return look()
    return f"Du kannst nicht nach {direction} gehen."


@mcp.tool(
    name="take",
    title="Nimm einen Gegenstand auf",
    description="Nimmt einen Gegenstand auf, falls vorhanden."
)
def take(item: str) -> str:
    room = world.WORLD[world.current_room]
    if item in room.items:
        room.items.remove(item)
        world.inventory.append(item)
        return f"Du hast '{item}' aufgenommen."
    return f"'{item}' gibt es hier nicht."


@mcp.tool(
    name="inventory",
    title="Zeige dein Inventar",
    description="Zeigt alle gesammelten Gegenstände."
)
def inventory_tool() -> str:
    if world.inventory:
        return f"In deinem Inventar: {', '.join(world.inventory)}"
    return "Dein Inventar ist leer."


@mcp.tool(
    name="use",
    title="Benutze einen Gegenstand",
    description="Benutzt einen Gegenstand am aktuellen Ort."
)
def use(item: str) -> str:
    if item not in world.inventory:
        return f"Du hast '{item}' nicht im Inventar."

    # --- AUFGABE 1: Coach Fergusons Auto reparieren ---
    if world.current_room == "parkplatz_baseballstadion" and item in REPAIR_TOOLS:
        used_repair_tools.add(item)
        world.inventory.remove(item)
        if used_repair_tools >= REPAIR_TOOLS:
            completed_tasks.add("car_fixed")
            return (
                "Du hebst das Auto an, löst die Bolzen und flickst den Reifen.\n"
                "Coach Ferguson schaut kurz rüber und nickt dir wortlos zu.\n"
                "Etwas in deiner Brust wird leichter."
            )
        remaining = REPAIR_TOOLS - used_repair_tools
        return f"Du verwendest {item}. Dir fehlen noch: {', '.join(remaining)}."

    # --- AUFGABE 2: D&D-Freunde versöhnen ---
    if world.current_room == "stadtbuecherei" and item == "dnd_brettspiel":
        completed_tasks.add("friends_reconciled")
        world.inventory.remove(item)
        return (
            "Du stellst das Brettspiel auf den alten Tisch.\n"
            "Die vertrauten Figuren erinnern dich an eure langen Spieleabende.\n"
            "Du hättest sie nie im Stich lassen sollen."
        )

    # --- AUFGABE 3: Opa Gerald ehren ---
    if world.current_room == "friedhof" and item == "jacobs_altes_handy":
        completed_tasks.add("grandpa_forgiven")
        world.inventory.remove(item)
        return (
            "Du öffnest die alten Sprachnachrichten auf dem Handy.\n"
            "Opa Geralds Stimme: 'Jacob, ich vermisse dich. Ruf mich an, wenn du kannst.'\n"
            "Du hast nie zurückgerufen. Tränen laufen über dein Gesicht."
        )

    if world.current_room == "friedhof" and item == "opas_altes_schnitzmesser":
        world.inventory.remove(item)
        return (
            "Du legst das Schnitzmesser sanft auf den Grabstein.\n"
            "Ein kleines Zeichen, dass du nicht vergessen hast."
        )

    # --- Garage aufschließen ---
    if world.current_room == "opas_haus" and item == "garage_schluessel":
        if "osten" not in world.WORLD["opas_haus"].exits:
            world.WORLD["opas_haus"].exits["osten"] = "opas_garage"
            world.WORLD["opas_haus"].description = "Das alte Haus deines Großvaters. Die Garage im Osten ist nun geöffnet."
            world.inventory.remove(item)
            return "Du schließt die Garage auf. Der Weg nach Osten ist frei."
        return "Die Garage ist bereits geöffnet."

    # --- Foto betrachten (bleibt im Inventar) ---
    if item == "foto_dnd_freunde":
        return "Du betrachtest das alte Foto. Vier Jungs um einen Tisch, lachend. Wann wurde es so kompliziert?"

    return f"Du weißt nicht, was du mit '{item}' an diesem Ort machen kannst."


if __name__ == "__main__":
    logger.info("MCP Server gestartet")
    mcp.run(transport="stdio")
