import ollama
from fastmcp import Client
from rich.console import Console

console = Console()

# MCP Client (lokal)
mcp_client = Client("http://localhost:8000/mcp")

# System Prompt laden
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

messages = [{"role": "system", "content": system_prompt}]

console.print("[bold red]🌲 SLENDER MAN - THE FOREST 🌲[/]")
console.print("[bold red]Du bist allein im Wald... Finde alle 8 Zettel und komm lebend zurück.[/]\n")

while True:
    user_input = console.input("\n[bold blue]Du > [/] ")
    
    if user_input.lower() in ["quit", "ende", "exit", "q"]:
        console.print("[red]Du rennst zurück zum Auto...[/]")
        break

    messages.append({"role": "user", "content": user_input})

    response = ollama.chat(
        model="gemma3:4",
        messages=messages,
        tools=mcp_client.tools(),
    )

    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            args = tool_call.function.arguments

            console.print(f"[dim]→ Tool: {tool_name}({args})[/dim]")

            result = mcp_client.call_tool(tool_name, args)

            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id
            })

            # Narrative Antwort vom LLM
            final_response = ollama.chat(
                model="gemma3:4",
                messages=messages
            )
            console.print(f"[bold red]Wald:[/] {final_response['message']['content']}")
            messages.append(final_response['message'])
    else:
        console.print(f"[bold red]Wald:[/] {response['message']['content']}")
        messages.append(response['message'])
