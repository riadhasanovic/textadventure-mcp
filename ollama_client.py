"""
Ollama Client - Für Jacob Miller Textadventure
"""
import os
import json
import httpx
import logging

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


SYSTEM_PROMPT = """
Du bist der Erzähler eines psychologischen Horror-Textadventures.
Der Spieler ist Jacob Miller. Er durchlebt seine eigenen Schuldgefühle.

Du darfst **nur** JSON ausgeben. Kein normaler Text.

Antworte immer mit einem gültigen JSON-Objekt:
{
  "tool": "name_des_tools",
  "arguments": { ... }
}

Verfügbare Tools: look, move, take, inventory

Bleib immer düster, atmosphärisch und psychologisch. Keine Witze, keine Emojis.
"""


async def ask_ollama(user_message: str, tools_description: str) -> dict | None:
    url = f"{BASE_URL}/api/chat"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Verfügbare Tools:\n{tools_description}"},
        {"role": "user", "content": user_message}
    ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json={
                    "model": MODEL,
                    "messages": messages,
                    "temperature": 0.0,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            answer = data["message"]["content"]
            return _parse_tool_call(answer)
        except Exception as e:
            logger.error(f"Fehler bei Ollama: {e}")
            return None


async def format_result(tool_name: str, result: str) -> str:
    """Macht aus dem Tool-Ergebnis eine atmosphärische Erzählung."""
    url = f"{BASE_URL}/api/chat"

    messages = [
        {"role": "system", "content": "Du bist ein düsterer, psychologischer Erzähler. Schreibe kurz, bedrückend und atmosphärisch auf Deutsch."},
        {"role": "user", "content": f"Das Tool '{tool_name}' hat folgendes Ergebnis geliefert:\n{result}"}
    ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json={"model": MODEL, "messages": messages, "temperature": 0.7, "stream": False}, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except Exception:
            return result


def _parse_tool_call(answer: str) -> dict | None:
    clean = answer.strip()
    if "```" in clean:
        clean = clean.split("```")[1].strip()
        if clean.startswith("json"):
            clean = clean[4:].strip()

    try:
        parsed = json.loads(clean)
        if isinstance(parsed, list) and len(parsed) > 0:
            parsed = parsed[0]
        if "tool" in parsed and "arguments" in parsed:
            return parsed
    except:
        pass
    return None