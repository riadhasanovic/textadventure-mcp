"""
Ollama Client - Strenge Version für Jacob Miller
"""
import os
import re
import json
import httpx
import logging

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")


SYSTEM_PROMPT = """You are the game engine for a German text adventure. Your only job is to decide which tool to call based on the player's input.

Respond ONLY with a JSON object in this exact format:
{"tool": "<tool_name>", "arguments": {<args>}}

Examples:
Input: geh nach norden → {"tool": "move", "arguments": {"direction": "norden"}}
Input: schau dich um   → {"tool": "look", "arguments": {}}
Input: nimm wagenheber → {"tool": "take", "arguments": {"item": "wagenheber"}}
Input: benutze handy   → {"tool": "use", "arguments": {"item": "jacobs_altes_handy"}}
Input: inventar        → {"tool": "inventory", "arguments": {}}

Never output prose, markdown, or explanations — only the JSON object."""


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
                json={"model": MODEL, "messages": messages, "temperature": 0.0, "stream": False, "format": "json"},
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

    if "GAME_OVER_GOOD" in result or "GAME_OVER_BAD" in result:
        return result

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


_PHONE_LISTEN_WORDS = frozenset({"anhören", "hören", "abspielen", "zuhören", "anhöre", "höre", "abspiele"})
_PHONE_DELETE_WORDS = frozenset({"löschen", "entfernen", "wegwerfen", "ignorieren", "verwerfen", "lösche"})

_PHOTO_VIEW_WORDS = frozenset({"betrachten", "anschauen", "ansehen", "angucken", "beobachten", "schauen", "gucken", "behalten", "anschaue", "ansehe"})
_PHOTO_BURN_WORDS = frozenset({"verbrennen", "anzünden", "abfackeln", "zerstören", "vernichten", "verbrenne", "anzünde"})


def _keyword_match(user_input: str, a_words: frozenset[str], b_words: frozenset[str]) -> str | None:
    tokens = set(re.sub(r"[^\wäöüÄÖÜß]", " ", user_input.lower()).split())
    has_a = bool(tokens & a_words)
    has_b = bool(tokens & b_words)
    if has_a and not has_b:
        return "a"
    if has_b and not has_a:
        return "b"
    return None


_PHONE_CHOICE_PROMPT = """Du klassifizierst Spielereingaben für ein deutsches Textadventure.
Die Entscheidung: Soll Jacob die Sprachnachrichten seines Opas anhören oder löschen?

Antworte NUR mit einem dieser drei JSON-Objekte — keine Erklärungen, kein Prosa:
{"choice": "phone_listen"}   — Eingabe bedeutet anhören/abspielen/hören/zuhören
{"choice": "phone_delete"}   — Eingabe bedeutet löschen/entfernen/wegwerfen/ignorieren/verwerfen
{"choice": "unclear"}        — Eingabe ist mehrdeutig oder unbekannt"""


async def classify_phone_choice(user_input: str) -> str:
    pre = _keyword_match(user_input, _PHONE_LISTEN_WORDS, _PHONE_DELETE_WORDS)
    if pre == "a":
        return "phone_listen"
    if pre == "b":
        return "phone_delete"

    url = f"{BASE_URL}/api/chat"
    messages = [
        {"role": "system", "content": _PHONE_CHOICE_PROMPT},
        {"role": "user", "content": user_input},
    ]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json={"model": MODEL, "messages": messages, "temperature": 0.0, "stream": False, "format": "json"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            parsed = json.loads(data["message"]["content"].strip())
            choice = parsed.get("choice", "unclear")
            return choice if choice in ("phone_listen", "phone_delete") else "unclear"
        except Exception as e:
            logger.error(f"Fehler bei Telefon-Klassifikation: {e}")
            return "unclear"


_PHOTO_CHOICE_PROMPT = """Du klassifizierst Spielereingaben für ein deutsches Textadventure.
Die Entscheidung: Soll Jacob das Foto anschauen oder verbrennen?

Antworte NUR mit einem dieser drei JSON-Objekte — keine Erklärungen, kein Prosa:
{"choice": "photo_view"}   — Eingabe bedeutet anschauen/betrachten/ansehen/behalten/beobachten
{"choice": "photo_burn"}   — Eingabe bedeutet verbrennen/anzünden/abfackeln/zerstören/verbrennen
{"choice": "unclear"}      — Eingabe ist mehrdeutig oder unbekannt"""


async def classify_photo_choice(user_input: str) -> str:
    pre = _keyword_match(user_input, _PHOTO_VIEW_WORDS, _PHOTO_BURN_WORDS)
    if pre == "a":
        return "photo_view"
    if pre == "b":
        return "photo_burn"

    url = f"{BASE_URL}/api/chat"
    messages = [
        {"role": "system", "content": _PHOTO_CHOICE_PROMPT},
        {"role": "user", "content": user_input},
    ]
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json={"model": MODEL, "messages": messages, "temperature": 0.0, "stream": False, "format": "json"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            parsed = json.loads(data["message"]["content"].strip())
            choice = parsed.get("choice", "unclear")
            return choice if choice in ("photo_view", "photo_burn") else "unclear"
        except Exception as e:
            logger.error(f"Fehler bei Foto-Klassifikation: {e}")
            return "unclear"


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
    except Exception:
        pass
    return None