from pydantic import BaseModel
from typing import Dict, List

class Room(BaseModel):
    name: str
    description: str
    exits: Dict[str, str]          # z.B. {"norden": "hoehle"}
    items: List[str] = []

# Einfache Welt (3–4 Räume reichen für den Anfang)
WORLD = {
    "lichtung": Room(
        name="Lichtung",
        description="Du stehst auf einer sonnigen Lichtung im Wald. Im Norden siehst du eine dunkle Höhle.",
        exits={"norden": "hoehle"},
        items=["stock"]
    ),
    "hoehle": Room(
        name="Höhle",
        description="Eine feuchte Höhle. Es liegt ein alter Schlüssel auf dem Boden.",
        exits={"sueden": "lichtung"},
        items=["schluessel"]
    )
}

# Startzustand
current_room = "lichtung"
inventory: List[str] = []