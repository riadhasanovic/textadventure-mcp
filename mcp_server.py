"""
MCP Server - Tools für Jacob Miller Textadventure
"""
from mcp.server.fastmcp import FastMCP
import json
import logging
import sys
import world
import glossary

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Jacob Miller")

# Tracks which of the three moral tasks Jacob has completed.
completed_tasks: set[str] = set()
# Tracks which repair tools have been used at the parking lot.
used_repair_tools: set[str] = set()
# Tracks which fog manifestations have already appeared this playthrough.
triggered_manifestations: set[str] = set()
# Whether the garage has been unlocked with the key.
garage_unlocked: bool = False

REPAIR_TOOLS = {"wagenheber", "reifen_reparaturset", "radkreuz"}
REQUIRED_TASKS = {"car_fixed", "friends_reconciled", "grandpa_forgiven"}

MANIFESTATIONS: dict[str, str] = {
    "dnd_friends": (
        "Aus dem Nebel treten vier Gestalten. Du erkennst ihre Gesichter,\n"
        "auch wenn ihre Konturen verschwimmen.\n"
        "'Auch wenn du uns vergessen hast, bist du immer unser Freund geblieben, Jacob...'\n"
        "Der Nebel schließt sich wieder über ihnen."
    ),
    "coach_ferguson": (
        "Coach Ferguson tritt aus dem Nebel. Sein Blick ist ernst, aber nicht hart.\n"
        "\"Du hättest viel erreichen können, Jacob. Doch dein Ego war größer als du selbst...\n"
        "Doch für den Weg der Besserung ist es noch nicht zu spät.\"\n"
        "Er nickt dir zu und verschwindet wieder im Nebel."
    ),
    "opa_gerald": (
        "Aus dem Nebel tritt dein Großvater. Sein Lächeln ist warm, wie du es in Erinnerung hast.\n"
        "\"Mein Junge, schön dass du mich besuchen kommst. Du brauchst dir wegen\n"
        "Vergangenem keine Gedanken zu machen. Ich vergebe dir, Jake.\"\n"
        "Er legt eine unsichtbare Hand auf deine Schulter, dann löst er sich langsam auf."
    ),
}


def _fog_manifestation(key: str) -> str:
    if key in triggered_manifestations:
        return ""
    triggered_manifestations.add(key)
    return f"\nFOG_MANIFESTATION_START\n{MANIFESTATIONS[key]}\nFOG_MANIFESTATION_END"


@mcp.tool(
    name="look",
    title="Beschreibe den aktuellen Ort",
    description="Zeigt den aktuellen Ort und alle erreichbaren Ziele."
)
def look() -> str:
    room = world.WORLD[world.current_room]

    glossary.discover(world.current_room)
    if world.current_room in ("friedhof", "opas_haus", "opas_garage"):
        glossary.discover("opa_gerald")
    if world.current_room == "mr_smiths_haus":
        glossary.discover("smith")

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

    description = room.description
    items_visible = room.items
    if world.current_room == "opas_garage" and not garage_unlocked:
        description = "Die Garagentür ist abgeschlossen. Durch das kleine Fenster siehst du Werkzeug und alte Kisten."
        items_visible = []

    output = [f"**{room.name}**", description, ""]

    if items_visible:
        output.append(f"Gegenstände hier: {', '.join(items_visible)}")
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
    if world.current_room == "opas_garage" and not garage_unlocked:
        return "Die Garage ist abgeschlossen. Du kommst nicht rein."
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

    # --- SCHLECHTES ENDE: Reifen aufschlitzen ---
    if world.current_room == "parkplatz_baseballstadion" and item == "opas_altes_schnitzmesser":
        world.inventory.remove(item)
        return (
            "Du starrst auf Coach Fergusons Auto.\n"
            "Etwas Dunkles steigt in dir auf — all der alte Groll, die unausgesprochene Wut.\n"
            "Bevor du es aufhalten kannst, greifst du zum Messer und stichst in die verbliebenen Reifen.\n"
            "Das Zischen der entweichenden Luft klingt wie ein letzter Atemzug.\n\n"
            "Coach Ferguson tritt hinter dem Auto hervor. Sein Gesicht ist wie Stein.\n"
            "'Jacob Miller.' Mehr sagt er nicht.\n\n"
            "Die Polizei kommt schneller als du denkst. Dein Traum von Lovers Leap — von allem —\n"
            "löst sich auf wie der Nebel am frühen Morgen.\n"
            "Manche Wunden heilt man nicht. Manche reißt man nur weiter auf.\n\n"
            "GAME_OVER_BAD"
        )

    # --- AUFGABE 1: Coach Fergusons Auto reparieren ---
    if world.current_room == "parkplatz_baseballstadion" and item in REPAIR_TOOLS:
        used_repair_tools.add(item)
        world.inventory.remove(item)
        if used_repair_tools >= REPAIR_TOOLS:
            completed_tasks.add("car_fixed")
            glossary.discover("coach_ferguson")
            return (
                "Du hebst das Auto an, löst die Bolzen und flickst den Reifen.\n"
                "Coach Ferguson schaut kurz rüber und nickt dir wortlos zu.\n"
                "Etwas in deiner Brust wird leichter."
                + _fog_manifestation("coach_ferguson")
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
            + _fog_manifestation("dnd_friends")
        )

    # --- AUFGABE 3: Opa Gerald ehren ---
    if world.current_room == "friedhof" and item == "jacobs_altes_handy":
        completed_tasks.add("grandpa_forgiven")
        world.inventory.remove(item)
        return (
            "Du öffnest die alten Sprachnachrichten auf dem Handy.\n"
            "Opa Geralds Stimme: 'Jacob, ich vermisse dich. Ruf mich an, wenn du kannst.'\n"
            "Du hast nie zurückgerufen. Tränen laufen über dein Gesicht."
            + _fog_manifestation("opa_gerald")
        )

    if world.current_room == "friedhof" and item == "opas_altes_schnitzmesser":
        world.inventory.remove(item)
        return (
            "Du legst das Schnitzmesser sanft auf den Grabstein.\n"
            "Ein kleines Zeichen, dass du nicht vergessen hast."
        )

    # --- Garage aufschließen ---
    if item == "garage_schluessel" and world.current_room in ("opas_haus", "opas_garage"):
        global garage_unlocked
        if garage_unlocked:
            return "Die Garage ist bereits geöffnet."
        garage_unlocked = True
        world.WORLD["opas_haus"].description = "Das alte Haus deines Großvaters. Die Garage im Osten ist nun geöffnet."
        world.WORLD["opas_garage"].description = "Hier hat dein Großvater gerne Sachen gebastelt. Als Jacob klein war, hat er oft stundenlang zugeschaut."
        world.inventory.remove(item)
        return "Du schließt die Garage auf. Die Tür schwingt auf."

    # --- Foto betrachten (bleibt im Inventar) ---
    if item == "foto_dnd_freunde":
        return "Du betrachtest das alte Foto. Vier Jungs um einen Tisch, lachend. Wann wurde es so kompliziert?"

    return f"Du weißt nicht, was du mit '{item}' an diesem Ort machen kannst."


@mcp.tool(
    name="glossar",
    title="Zeige das Glossar",
    description="Gibt alle bisher entdeckten Personen und Orte als JSON zurück."
)
def glossar_tool() -> str:
    return json.dumps(glossary.get_discovered(), ensure_ascii=False)


if __name__ == "__main__":
    logger.info("MCP Server gestartet")
    mcp.run(transport="stdio")
