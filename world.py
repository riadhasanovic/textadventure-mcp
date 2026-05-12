from pydantic import BaseModel
from typing import Dict, List

class Room(BaseModel):
    name: str
    description: str
    exits: Dict[str, str]
    items: List[str] = []

WORLD = {
    "lichtung": Room(
        name="Verlassene Lichtung",
        description="Dein Auto steht kaputt auf einer kleinen Lichtung. Es ist mitten in der Nacht und stockdunkel.",
        exits={"norden": "waldpfad", "osten": "alter_baum"},
        items=[]
    ),
    "waldpfad": Room(
        name="Schmaler Waldpfad",
        description="Ein enger Pfad führt tiefer in den Wald. Du hörst Äste knacken.",
        exits={"sueden": "lichtung", "norden": "tiefer_wald", "westen": "nebelwald"},
        items=["zettel_1"]
    ),
    "alter_baum": Room(
        name="Der alte knorrige Baum",
        description="Ein riesiger, verdrehter Baum. Die Rinde sieht aus wie verzerrte Gesichter.",
        exits={"westen": "lichtung", "osten": "ruine"},
        items=["zettel_2"]
    ),
    "tiefer_wald": Room(
        name="Tiefer Wald",
        description="Hier ist es fast komplett dunkel. Du fühlst dich beobachtet.",
        exits={"sueden": "waldpfad", "osten": "see"},
        items=["zettel_3"]
    ),
    "nebelwald": Room(
        name="Nebelwald",
        description="Dichter Nebel wabert zwischen den Bäumen.",
        exits={"osten": "waldpfad", "norden": "verlassene_huette"},
        items=["zettel_4"]
    ),
    "ruine": Room(
        name="Alte Ruine",
        description="Überreste eines alten Gebäudes.",
        exits={"westen": "alter_baum", "norden": "see"},
        items=["zettel_5"]
    ),
    "see": Room(
        name="Schwarzer See",
        description="Ein stiller, pechschwarzer See.",
        exits={"westen": "tiefer_wald", "sueden": "ruine"},
        items=["zettel_6"]
    ),
    "verlassene_huette": Room(
        name="Verlassene Hütte",
        description="Eine alte, verfallene Jagdhütte.",
        exits={"sueden": "nebelwald"},
        items=["zettel_7"]
    ),
    "geheime_kammer": Room(
        name="Geheime Kammer",
        description="Ein versteckter Raum unter der Hütte.",
        exits={"sueden": "verlassene_huette"},
        items=["zettel_8"]
    )
}

current_room: str = "lichtung"
inventory: List[str] = []
collected_notes: int = 0
