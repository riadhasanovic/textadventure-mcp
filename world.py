from pydantic import BaseModel
from typing import Dict, List

class Room(BaseModel):
    name: str
    description: str
    exits: Dict[str, str] = {}
    items: List[str] = []

WORLD = {
    "alter_baum": Room(
        name="Der alte Baum",
        description="Du wachst unter einem riesigen, knorrigen alten Baum auf. Der Nebel ist dicht.",
        exits={
            "norden": "parkplatz_baseballstadion",
            "süden": "jacobs_haus",
            "osten": "friedhof",
            "westen": "stadtbuecherei"
        },
        items=["opas_altes_schnitzmesser"]
    ),

    "jacobs_haus": Room(
        name="Jacobs Haus",
        description="Dein eigenes Haus. Die Tür steht offen.",
        exits={
            "osten": "lovers_leap",
            "westen": "stadtbuecherei",
            "norden": "alter_baum"
        },
        items=["dnd_brettspiel"]
    ),

    "highschool": Room(
        name="Highschool",
        description="Deine alte Highschool.",
        exits={
            "süden": "stadtbuecherei",
            "norden": "mr_smiths_haus"
        },
        items=[]
    ),

    "stadtbuecherei": Room(
        name="Stadtbibliothek",
        description="Die alte Stadtbibliothek. Hier ist der Treffpunkt gewesen für dich und deine Freunde um D&D zu spielen.",
        exits={
            "norden": "highschool",
            "osten": "alter_baum",
            "süden": "jacobs_haus"
        },
        items=["foto_dnd_freunde"]
    ),

    "mr_smiths_haus": Room(
        name="Haus von Hausmeister Smith",
        description="Das Haus von Hausmeister Smith, hier findest du bestimmt verschiedene Werkzeuge.",
        exits={
            "süden": "highschool",
            "osten": "parkplatz_baseballstadion"
        },
        items=["wagenheber", "reifen_reparaturset", "radkreuz"]
    ),

    "parkplatz_baseballstadion": Room(
        name="Parkplatz am Baseballstadion",
        description="Hier steht das Auto von Coach Ferguson, welches Jacob reparieren muss, um zum Lovers Leap zu kommen.",
        exits={
            "westen": "mr_smiths_haus",
            "süden": "alter_baum",
            "osten": "opas_haus"
        },
        items=[]
    ),

    "friedhof": Room(
        name="Friedhof",
        description="Der Friedhof, auf dem dein Opa begraben liegt.",
        exits={
            "norden": "opas_haus",
            "osten": "lovers_leap",
            "westen": "alter_baum"
        },
        items=[]
    ),

    "opas_haus": Room(
        name="Haus von Opa Gerald",
        description="Das alte Haus deines Großvaters.",
        exits={
            "westen": "friedhof",
            "osten": "opas_garage",
        },
        items=["garage_schluessel"]
    ),


    "opas_garage": Room(
        name="Garage von Opa Gerald.",
        description="Hier hat er gerne Sachen gebastelt für Jacob als er klein war.",
        exits={
            "westen": "opas_haus"
        },
        items=["jacobs_altes_handy"]
    ),

    "lovers_leap": Room(
        name="Lovers Leap",
        description="Der höchste Punkt der Stadt. Von hier aus siehst du alles.",
        exits={"westen": "alter_baum"},
        items=[]
    )
}

# Globaler Spielzustand
current_room: str = "alter_baum"
inventory: List[str] = []