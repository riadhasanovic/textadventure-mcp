import ollama
from fastmcp import Client
from rich.console import Console
import json

console = Console()

# MCP-Client verbinden
mcp_client = Client("http://localhost:8000")

# System-Prompt laden
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

messages = [{"role": "system", "content": system_prompt}]

console.print("[bold green]Textadventure gestartet! Schreibe 'quit' zum Beenden.[/]")

while True:
    user_input = console.input("\n[bold blue]Du:[/] ")
    if user_input.lower() in ["quit", "ende", "exit"]:
        break

    messages.append({"role": "user", "content": user_input})

    # An Ollama mit Tool-Calling schicken
    response = ollama.chat(
        model="gemma3:4",           # oder gemma3:4b falls du das hast
        messages=messages,
        tools=mcp_client.tools(),   # hier kommen automatisch alle MCP-Tools rein!
        format="json"               # hilft gemma3 bei Tool-Calls
    )

    # Tool-Calls ausführen (falls welche da sind)
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            args = tool_call.function.arguments

            console.print(f"[dim]→ Tool Call: {tool_name}({args})[/dim]")

            result = mcp_client.call_tool(tool_name, args)

            # Ergebnis zurück ans LLM
            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id
            })

            # Neue Antwort vom LLM holen (narrativ)
            final_response = ollama.chat(
                model="gemma3:4",
                messages=messages
            )
            console.print(f"[bold green]Erzähler:[/] {final_response['message']['content']}")
            messages.append(final_response['message'])
    else:
        # Falls das LLM direkt antwortet (selten)
        console.print(f"[bold green]Erzähler:[/] {response['message']['content']}")
        messages.append(response['message'])