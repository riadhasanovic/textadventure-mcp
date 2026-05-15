from pydantic import BaseModel
from typing import Dict, List

class Room(BaseModel):
    name: str
    description: str
    exits: Dict[str, str]
    items: List[str] = []

# ==================== JACOB MILLER - LOVERS LEAP ====================
WORLD = {
    "jacobs_house": Room(
        name="Jacobs Haus",
        description="Deine Auffahrt. Du wachst hier auf. Es ist neblig, kalt und unheimlich still.",
        exits={"norden": "library", "osten": "high_school"},
        items=[]
    ),

    "library": Room(
        name="Stadtbibliothek",
        description="Die alte Bibliothek. Hier steht noch der alte D&D-Tisch deiner früheren Freunde David, Zack und Billy.",
        exits={"sueden": "jacobs_house", "osten": "high_school"},
        items=["foto_dnd_freunde"]
    ),

    "high_school": Room(
        name="High School",
        description="Deine alte Highschool. Der Eingang ist offen. Der Weg zum Trainingsplatz führt nach Osten.",
        exits={"westen": "library", "osten": "trainingsplatz"},
        items=[]
    ),

    "trainingsplatz": Room(
        name="Football Trainingsplatz",
        description="Der verlassene Trainingsplatz. In der Nähe steht das Auto von Coach Ferguson.",
        exits={"westen": "high_school", "sueden": "parkplatz"},
        items=[]
    ),

    "parkplatz": Room(
        name="Parkplatz",
        description="Das Auto von Coach Ferguson steht hier. Einer der Reifen ist zerstochen.",
        exits={"norden": "trainingsplatz"},
        items=["baseballjacke"]
    ),

    "hh_smith_house": Room(
        name="Haus von H.H. Smith",
        description="Die Garage von Hausmeister Smith neben dem Sportplatz.",
        exits={"norden": "trainingsplatz"},
        items=["wagenheber", "radkreuz", "reifenreparatursatz"]
    ),

    "opas_house": Room(
        name="Opas Haus",
        description="Das alte Haus deines Großvaters. Unter dem Fußabtreter liegt ein Schlüssel.",
        exits={"osten": "garage_opa"},
        items=["garage_schluessel"]
    ),

    "garage_opa": Room(
        name="Garage von Opa Garry",
        description="Hier hat dein Opa früher viel für dich gebaut. Dein altes Handy liegt in einer Schublade.",
        exits={"westen": "opas_house"},
        items=["altes_handy"]
    ),

    "friedhof": Room(
        name="Friedhof",
        description="Der Friedhof, auf dem dein Opa begraben liegt. Von hier führt ein Weg hinauf zu Lovers Leap.",
        exits={"westen": "opas_house", "norden": "lovers_leap"},
        items=[]
    ),

    "lovers_leap": Room(
        name="Lovers Leap",
        description="Der höchste Punkt der Stadt. Von hier aus siehst du alles. Hier wird sich alles entscheiden...",
        exits={"sueden": "friedhof"},
        items=[]
    )
}

# Globaler Spielzustand
current_room: str = "jacobs_house"
inventory: List[str] = []
collected_fragments: int = 0