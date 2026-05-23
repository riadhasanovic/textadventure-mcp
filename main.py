"""
Finale Hauptprogramm - Jacob Miller Textadventure (stabil)
"""
import sys
import json
import logging
import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text

from mcp_connector import MCPConnector
from ollama_client import ask_ollama, format_result, classify_phone_choice, classify_photo_choice

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

console = Console(record=True)


def render_room(text: str):
    lines = text.strip().split("\n")
    title = ""
    body_lines = lines
    first = lines[0] if lines else ""
    if first.startswith("**") and first.endswith("**"):
        title = first[2:-2]
        body_lines = lines[1:]
    body = Markdown("\n".join(body_lines).strip())
    console.print(Panel(body, title=f"[bold]{title}[/]", padding=(0, 1)))


def render_inventory(text: str):
    if "leer" in text.lower() or ":" not in text:
        console.print(Panel(Text("Dein Inventar ist leer.", style="dim"), title="[bold]Inventar[/]"))
        return
    items_part = text.split(":", 1)[1].strip()
    items = [i.strip() for i in items_part.split(",") if i.strip()]
    table = Table(title="Inventar", show_lines=True, highlight=False)
    table.add_column("Gegenstand", style="default", no_wrap=True)
    table.add_column("Beschreibung", style="default")
    for item in items:
        display = item.replace("_", " ").title()
        table.add_row(display, "")
    console.print(table)


def _is_room_output(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("**") and "\n" in stripped


def render_glossary(text: str):
    entries = json.loads(text)
    if not entries:
        console.print(Panel(Text("Noch keine Einträge entdeckt.", style="dim"), title="[bold]Glossar[/]"))
        return
    table = Table(show_header=True, show_lines=True, padding=(0, 1), highlight=False)
    table.add_column("Name", style="default", no_wrap=True, min_width=22)
    table.add_column("Beschreibung", style="default")
    current_category = None
    for entry in entries:
        if entry["category"] != current_category:
            current_category = entry["category"]
            label = "Personen" if current_category == "Person" else "Orte"
            table.add_row(f"── {label} ──", "", style="dim")
        table.add_row(entry["name"], entry["description"])
    console.print(Panel(table, title="[bold]Glossar[/]", padding=(0, 0)))


def render_response(text: str):
    console.print(Markdown(text))


def _extract_manifestation(text: str) -> tuple[str, str | None]:
    start = "FOG_MANIFESTATION_START"
    end = "FOG_MANIFESTATION_END"
    if start in text and end in text:
        before = text[:text.index(start)].rstrip()
        fog = text[text.index(start) + len(start):text.index(end)].strip()
        return before, fog
    return text, None


def render_fog_manifestation(text: str):
    console.print()
    console.print(text, style="dim italic white")
    console.print()


async def main():
    console.print(Panel(
        Text("LOVERS LEAP", justify="center", style="bold"),
        padding=(1, 4),
    ))
    console.print()
    console.print(Markdown(
        "Du wachst unter dem alten Baum im Zentrum der Stadt auf. "
        "Der Nebel ist dicht, und die Welt um dich herum wirkt fremd und doch vertraut.\n\n"
        "In der Ferne hörst du das Flattern von Krähen..."
    ))
    console.print()
    console.print("[dim]Tipp 'hilfe', wenn du nicht weiter weißt.[/dim]")

    connector = MCPConnector()
    awaiting_phone_choice = False
    awaiting_photo_choice = False

    async with connector.connect():
        while True:
            try:
                user_input = input("Du > ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ["quit", "ende", "exit", "q"]:
                console.print("\n[dim]Du gibst auf...[/dim]")
                break

            if user_input.lower() in ["hilfe", "befehle", "help"]:
                print_help()
                continue

            if user_input.lower() in ["glossar", "glossary"]:
                result = await connector.call_tool("glossar", {})
                render_glossary(result.output if result.success else "[]")
                continue

            if awaiting_phone_choice:
                choice = await classify_phone_choice(user_input)
                if choice == "phone_listen":
                    result = await connector.call_tool("phone_listen", {})
                    response = result.output if result.success else "Etwas stimmt nicht..."
                    awaiting_phone_choice = False
                elif choice == "phone_delete":
                    result = await connector.call_tool("phone_delete", {})
                    response = result.output if result.success else "Etwas stimmt nicht..."
                    awaiting_phone_choice = False
                else:
                    response = "Ich verstehe nicht ganz. Möchtest du die Nachrichten anhören oder löschen?"
            elif awaiting_photo_choice:
                choice = await classify_photo_choice(user_input)
                if choice == "photo_view":
                    result = await connector.call_tool("photo_view", {})
                    response = result.output if result.success else "Etwas stimmt nicht..."
                    awaiting_photo_choice = False
                elif choice == "photo_burn":
                    result = await connector.call_tool("photo_burn", {})
                    response = result.output if result.success else "Etwas stimmt nicht..."
                    awaiting_photo_choice = False
                else:
                    response = "Ich verstehe nicht ganz. Möchtest du das Foto betrachten oder verbrennen?"
            else:
                response = await process_request(connector, user_input)

            if "AWAITING_PHONE_CHOICE" in response:
                response = response.replace("AWAITING_PHONE_CHOICE", "").strip()
                awaiting_phone_choice = True
            if "AWAITING_PHOTO_CHOICE" in response:
                response = response.replace("AWAITING_PHOTO_CHOICE", "").strip()
                awaiting_photo_choice = True

            lower_cmd = user_input.lower()

            main_response, fog = _extract_manifestation(response)

            if "GAME_OVER_GOOD" in main_response:
                clean = main_response.replace("GAME_OVER_GOOD", "").strip()
                render_response(clean)
                console.print(Panel(
                    Text("GUTES ENDE: Der Nebel löst sich auf. Jacob ist frei.", justify="center", style="bold"),
                ))
                break
            elif "GAME_OVER_BAD" in main_response:
                clean = main_response.replace("GAME_OVER_BAD", "").strip()
                render_response(clean)
                console.print(Panel(
                    Text("Die Krähen zwingen dich zurück. Die Schleife beginnt von vorn...", justify="center", style="bold"),
                ))
                break
            elif lower_cmd in ["inventar", "inventory"]:
                render_inventory(main_response)
            elif _is_room_output(main_response):
                render_room(main_response)
            else:
                render_response(main_response)

            if fog:
                render_fog_manifestation(fog)


def print_help():
    table = Table(show_header=False, padding=(0, 1), highlight=False)
    table.add_column("Befehl", style="default", no_wrap=True)
    table.add_column("Beschreibung", style="default")
    table.add_row("schau dich um", "Beschreibt den aktuellen Ort")
    table.add_row("geh nach [norden|süden|osten|westen]", "Bewege dich in eine Richtung")
    table.add_row("nimm [gegenstand]", "Nimmt einen Gegenstand auf")
    table.add_row("benutze [gegenstand]", "Benutze einen Gegenstand")
    table.add_row("inventar", "Zeigt dein Inventar")
    table.add_row("glossar", "Zeigt entdeckte Personen und Orte")
    table.add_row("hilfe", "Zeigt diese Hilfe")
    table.add_row("quit / ende / exit", "Spiel beenden")
    console.print(Panel(table, title="[bold]Verfügbare Befehle[/]"))


async def process_request(connector: MCPConnector, user_input: str) -> str:
    lower = user_input.lower()

    if lower.startswith("schau dich um") or lower == "look":
        result = await connector.call_tool("look", {})
        return result.output if result.success else "Etwas stimmt nicht..."

    if lower == "inventar" or lower == "inventory":
        result = await connector.call_tool("inventory", {})
        return result.output if result.success else "Dein Inventar ist leer."

    if lower.startswith("geh nach ") or lower.startswith("move "):
        direction = lower.replace("geh nach ", "").replace("move ", "").strip()
        result = await connector.call_tool("move", {"direction": direction})
        return result.output if result.success else "Dorthin führt kein Weg."

    if lower.startswith("nimm "):
        item = lower.replace("nimm ", "").strip()
        result = await connector.call_tool("take", {"item": item})
        return result.output if result.success else f"'{item}' gibt es hier nicht."

    if lower.startswith("benutze ") or lower.startswith("use "):
        item = lower.replace("benutze ", "").replace("use ", "").strip()
        result = await connector.call_tool("use", {"item": item})
        return result.output if result.success else f"Du kannst '{item}' nicht benutzen."

    tool_call = await ask_ollama(user_input, connector.get_tools_description())
    if not tool_call:
        return "Die Krähen flattern unruhig..."

    tool_name = tool_call.get("tool")
    arguments = tool_call.get("arguments", {})

    result = await connector.call_tool(tool_name, arguments)

    if not result.success:
        return f"Etwas stimmt nicht... {result.error}"

    formatted = await format_result(tool_name, result.output)
    return formatted


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[dim]Die Krähen verstummen...[/dim]")
    except Exception as e:
        console.print(f"\nFehler: {e}")
