"""
Glossar - Orte und Personen im Jacob-Miller-Textadventure.
Einträge werden durch Spielfortschritt freigeschaltet.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class GlossaryEntry:
    id: str
    category: str  # "Person" or "Ort"
    name: str
    description: str


ENTRIES: Dict[str, GlossaryEntry] = {
    # --- Personen ---
    "jacob": GlossaryEntry(
        "jacob", "Person", "Jacob Miller",
        "Der Protagonist. Jacob wächst in Lovers Leap auf und kämpft mit "
        "ungelösten Schuldgefühlen aus seiner Vergangenheit."
    ),
    "opa_gerald": GlossaryEntry(
        "opa_gerald", "Person", "Opa Gerald",
        "Jacobs Großvater. Starb, bevor Jacob zurückrufen konnte. "
        "Seine Stimme lebt in alten Sprachnachrichten fort."
    ),
    "smith": GlossaryEntry(
        "smith", "Person", "Hausmeister Smith",
        "Der stille Hausmeister der Highschool. Sein Haus birgt Werkzeuge, "
        "die Jacob braucht, um sich seiner Schuld zu stellen."
    ),
    "coach_ferguson": GlossaryEntry(
        "coach_ferguson", "Person", "Coach Ferguson",
        "Der Baseballtrainer der Highschool. Jacob hat ihm nie gedankt "
        "und schuldet ihm mehr als nur eine Reifenpanne."
    ),

    # --- Orte ---
    "alter_baum": GlossaryEntry(
        "alter_baum", "Ort", "Der alte Baum",
        "Der riesige, knorrige Baum im Herzen von Lovers Leap. "
        "Hier beginnt Jacobs Schleife — und vielleicht endet sie hier auch."
    ),
    "jacobs_haus": GlossaryEntry(
        "jacobs_haus", "Ort", "Jacobs Haus",
        "Das vertraute Elternhaus. Die Tür steht immer offen, "
        "aber etwas hat sich verändert."
    ),
    "highschool": GlossaryEntry(
        "highschool", "Ort", "Highschool",
        "Jacobs alte Schule. Hier entstanden Freundschaften — und Schuldgefühle."
    ),
    "stadtbuecherei": GlossaryEntry(
        "stadtbuecherei", "Ort", "Stadtbibliothek",
        "Der Treffpunkt für D&D-Abende. Ein Ort voller gemeinsamer Erinnerungen, "
        "die Jacob lieber vergessen hätte."
    ),
    "mr_smiths_haus": GlossaryEntry(
        "mr_smiths_haus", "Ort", "Haus von Hausmeister Smith",
        "Das bescheidene Haus am Rand der Stadt. "
        "Werkzeuge für jeden Zweck hängen ordentlich an der Wand."
    ),
    "parkplatz_baseballstadion": GlossaryEntry(
        "parkplatz_baseballstadion", "Ort", "Parkplatz am Baseballstadion",
        "Der staubige Parkplatz neben dem Baseballfeld. "
        "Coach Fergusons Auto wartet mit einem platten Reifen."
    ),
    "friedhof": GlossaryEntry(
        "friedhof", "Ort", "Friedhof",
        "Stiller Ort am Rande von Lovers Leap. Opa Gerald liegt hier begraben. "
        "Jacob ist seit dem Begräbnis nicht mehr hier gewesen."
    ),
    "opas_haus": GlossaryEntry(
        "opas_haus", "Ort", "Haus von Opa Gerald",
        "Das alte Haus des Großvaters. Zeit scheint hier stehengeblieben zu sein — "
        "der Geruch nach Holz und alten Büchern ist noch da."
    ),
    "opas_garage": GlossaryEntry(
        "opas_garage", "Ort", "Garage von Opa Gerald",
        "Opas stille Werkstatt. Hier hat er für Jacob gebastelt, als er klein war. "
        "Ein Handy liegt auf der Werkbank."
    ),
    "lovers_leap": GlossaryEntry(
        "lovers_leap", "Ort", "Lovers Leap",
        "Der höchste Punkt der Stadt. Von hier siehst du alles — "
        "und musst dich allem stellen, was du hinter dir gelassen hast."
    ),
}

# Jacob ist von Anfang an bekannt.
discovered: set[str] = {"jacob", "alter_baum"}


def discover(entry_id: str) -> None:
    if entry_id in ENTRIES:
        discovered.add(entry_id)


def is_discovered(entry_id: str) -> bool:
    return entry_id in discovered


def get_discovered() -> List[dict]:
    order = ["Person", "Ort"]
    result = []
    for category in order:
        for entry in ENTRIES.values():
            if entry.id in discovered and entry.category == category:
                result.append({
                    "id": entry.id,
                    "category": entry.category,
                    "name": entry.name,
                    "description": entry.description,
                })
    return result
