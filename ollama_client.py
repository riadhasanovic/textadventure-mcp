"""
Ollama Client - Strenge Version für Jacob Miller
"""
import os
import json
import httpx
import logging

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


SYSTEM_PROMPT = """
Du bist ein nüchterner, direkter Erzähler eines Textadventures.
Schreibe **kurz, sachlich und in der Gegenwartsform**.
Maximal 2–3 kurze Sätze. Keine Poesie, keine Metaphern, keine langen Beschreibungen.
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
                json={"model": MODEL, "messages": messages, "temperature": 0.0, "stream": False},
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
    """Sehr strikte Formatierung – besonders für inventory und look"""
    if tool_name == "inventory":
        return result  # Direkte Ausgabe ohne LLM

    # Für look und andere Tools extrem kurz halten
    url = f"{BASE_URL}/api/chat"
    messages = [
        {"role": "system", "content": "Antworte extrem kurz und sachlich. Maximal 2 Sätze. Keine Poesie. Gegenwartsform."},
        {"role": "user", "content": result}
    ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json={"model": MODEL, "messages": messages, "temperature": 0.2, "stream": False}, timeout=20.0)
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