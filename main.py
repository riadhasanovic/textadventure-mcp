"""
Finale Hauptprogramm - Jacob Miller Textadventure (stabil)
"""
import sys
import logging
import asyncio

from mcp_connector import MCPConnector
from ollama_client import ask_ollama, format_result

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

async def main():
    print("=" * 75)
    print("                  LOVERS LEAP")
    print("=" * 75)
    print()
    print("Du wachst unter dem alten Baum im Zentrum der Stadt auf. Der Nebel ist dicht, und die Welt um dich herum wirkt fremd und doch vertraut.")
    print("In der Ferne hörst du das Flattern von Krähen...")
    print()
    print("Tipp 'hilfe', wenn du nicht weiter weißt.\n")

    connector = MCPConnector()

    async with connector.connect():
        while True:
            try:
                user_input = input("\nDu > ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ["quit", "ende", "exit", "q"]:
                print("\nDu gibst auf...")
                break

            if user_input.lower() in ["hilfe", "befehle", "help"]:
                print_help()
                continue

            response = await process_request(connector, user_input)
            print(f"\nWelt: {response}")


def print_help():
    print("\n" + "-"*60)
    print("Verfügbare Befehle:")
    print("  schau dich um          → Beschreibt den aktuellen Ort")
    print("  geh nach norden        → Bewege dich (norden, süden, osten, westen)")
    print("  nimm [gegenstand]      → Nimmt einen Gegenstand auf")
    print("  inventar               → Zeigt dein Inventar")
    print("  hilfe                  → Zeigt diese Hilfe")
    print("  in hand [gegenstand]   → Nimm einen Gegenstand in die Hand")
    print("  quit / ende / exit     → Spiel beenden")
    print("-"*60)


async def process_request(connector: MCPConnector, user_input: str) -> str:
    # Direkte Behandlung einfacher Befehle, damit es stabil läuft
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

    # Für alles andere den LLM verwenden
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
        print("\n\nDie Krähen verstummen...")
    except Exception as e:
        print(f"\nFehler: {e}")