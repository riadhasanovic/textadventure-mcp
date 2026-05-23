from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class Room(BaseModel):
    model_config = ConfigDict(validate_assignment=True, frozen=False)
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
        description=(
            "Deine alte Highschool. Am Westeingang stehst du, wo damals einige "
            "mit dem Rauchen begonnen haben."
        ),
        exits={
            "süden": "stadtbuecherei",
            "norden": "mr_smiths_haus"
        },
        items=["feuerzeug"]
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
        description="Hier steht das Auto von Coach Ferguson.",
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
        description="Das alte Haus deines Großvaters. Die Garage im Osten ist verschlossen.",
        exits={
            "westen": "friedhof",
            "norden": "parkplatz_baseballstadion",
            "osten": "opas_garage",
        },
        items=["garage_schluessel"]
    ),


    "opas_garage": Room(
        name="Garage von Opa Gerald",
        description="Die Garagentür ist abgeschlossen. Durch das kleine Fenster siehst du Werkzeug und alte Kisten.",
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

ITEMS: Dict[str, str] = {
    "opas_altes_schnitzmesser": "Ein abgewetztes Schnitzmesser. Der Griff ist von Opas Händen glattgescheuert.",
    "dnd_brettspiel": "Euer altes D&D-Brettspiel. Die Würfel klappern noch im Karton.",
    "foto_dnd_freunde": "Ein vergilbtes Foto. Vier Jungs um einen Tisch, lachend.",
    "wagenheber": "Ein robuster Wagenheber. Schwer, aber zuverlässig.",
    "reifen_reparaturset": "Ein Reifen-Reparaturset. Alles drin, um einen platten Reifen zu flicken.",
    "radkreuz": "Ein Radkreuz aus Stahl. Damit lösen sich selbst festsitzende Radmuttern.",
    "garage_schluessel": "Ein kleiner, rostiger Schlüssel. Er öffnet Opas Garage.",
    "jacobs_altes_handy": "Dein altes Handy. Der Akku hält noch – gerade so.",
    "feuerzeug": "Ein billiges Einwegfeuerzeug, schon halb leer.",
}

# Globaler Spielzustand
current_room: str = "alter_baum"
inventory: List[str] = []