"""
Hauptprogramm - Jacob Miller Textadventure
"""
import sys
import logging
import asyncio

from mcp_connector import MCPConnector
from ollama_client import ask_ollama, format_result

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


async def main():
    print("=" * 70)
    print("                  JACOB MILLER")
    print("                  LOVERS LEAP")
    print("=" * 70)
    print()
    print("Du wachst auf deiner eigenen Auffahrt auf.")
    print("Es ist neblig, kalt und unnatürlich still.")
    print("In der Ferne hörst du das Flattern von Krähen.")
    print("Sie beobachten dich.")
    print()
    print("Du erinnerst dich vage: Du wolltest auf den Lovers Leap – den Hügel, von dem aus man die ganze Stadt sieht.")
    print()

    connector = MCPConnector()

    async with connector.connect():
        print("Die Krähen beobachten dich weiter...\n")

        while True:
            try:
                user_input = input("\nDu > ").strip()
            except EOFError:
                break

            if not user_input:
                continue
            if user_input.lower() in ["quit", "ende", "exit", "q"]:
                print("\nDu gibst auf und kehrst um...")
                break

            response = await process_request(connector, user_input)
            print(f"\nWelt: {response}")


async def process_request(connector: MCPConnector, user_input: str) -> str:
    tool_call = await ask_ollama(user_input, connector.get_tools_description())

    if not tool_call:
        return "Die Krähen flattern unruhig in den Bäumen..."

    tool_name = tool_call["tool"]
    arguments = tool_call["arguments"]

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