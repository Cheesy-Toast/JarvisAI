"""skills.py - het brein van Jarvis (Ali).

Eén functie is belangrijk voor de rest van het project:
    verwerk(opdracht) -> antwoord (string)

Een nieuwe skill toevoegen gaat in twee stappen:
    1. Schrijf een functie die `opdracht` ontvangt en een string teruggeeft.
    2. Zet een regel in de lijst COMMANDOS onderaan dit bestand.
"""
import random
import re
import webbrowser
from datetime import datetime
from urllib.parse import quote

import requests

NOTITIEBESTAND = "notities.txt"

STAD = "Groningen"
LATITUDE = 53.22
LONGITUDE = 6.57

DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]

GRAPPEN = [
    "Waarom nam de programmeur een ladder mee? Voor de high-level language.",
    "Er zijn 10 soorten mensen: zij die binair begrijpen en zij die dat niet doen.",
    "Waarom houden programmeurs niet van de natuur? Te veel bugs.",
    "Ik heb een grap over UDP, maar je krijgt hem misschien niet.",
]

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "nu.nl": "https://www.nu.nl",
    "nos": "https://nos.nl",
}


def begroeting(opdracht):
    return "Hoi! Waar kan ik mee helpen?"


def naam(opdracht):
    return "Ik ben Jarvis, een assistent gemaakt in Python door ons projectteam."


def tijd(opdracht):
    return datetime.now().strftime("Het is %H:%M")


def datum(opdracht):
    nu = datetime.now()
    return f"Het is {DAGEN[nu.weekday()]} {nu.day} {MAANDEN[nu.month - 1]} {nu.year}"


def grap(opdracht):
    return random.choice(GRAPPEN)


def open_website(opdracht):
    for sitenaam, url in WEBSITES.items():
        if sitenaam in opdracht:
            webbrowser.open(url)
            return f"Ik open {sitenaam} voor je."
    return "Welke website bedoel je? Ik ken: " + ", ".join(WEBSITES) + "."


def weer(opdracht):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"
    )
    try:
        data = requests.get(url, timeout=5).json()["current_weather"]
        return (f"In {STAD} is het nu {round(data['temperature'])} graden "
                f"en de wind is {round(data['windspeed'])} kilometer per uur.")
    except (requests.RequestException, KeyError, ValueError):
        return "Ik kan het weer nu niet ophalen. Heb je internet?"


def rekenen(opdracht):
    tekst = (opdracht.replace("gedeeld door", "/").replace("plus", "+")
             .replace("minus", "-").replace("min", "-")
             .replace("keer", "*").replace(",", "."))
    gevonden = re.search(r"(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)", tekst)
    if not gevonden:
        return "Zeg bijvoorbeeld: reken 5 plus 3."
    a, teken, b = float(gevonden.group(1)), gevonden.group(2), float(gevonden.group(3))
    if teken == "+":
        uitkomst = a + b
    elif teken == "-":
        uitkomst = a - b
    elif teken == "*":
        uitkomst = a * b
    else:
        if b == 0:
            return "Delen door nul kan niet."
        uitkomst = a / b
    if uitkomst == int(uitkomst):
        uitkomst = int(uitkomst)
    return f"De uitkomst is {uitkomst}"


def notitie_opslaan(opdracht):
    inhoud = opdracht.split("onthoud", 1)[1].strip()
    if inhoud.startswith("dat "):
        inhoud = inhoud[4:]
    if not inhoud:
        return "Wat moet ik onthouden?"
    with open(NOTITIEBESTAND, "a", encoding="utf-8") as bestand:
        bestand.write(inhoud + "\n")
    return "Goed, ik heb het genoteerd."


def notities_lezen(opdracht):
    try:
        with open(NOTITIEBESTAND, encoding="utf-8") as bestand:
            regels = [r.strip() for r in bestand if r.strip()]
    except FileNotFoundError:
        regels = []
    if not regels:
        return "Je hebt nog geen notities."
    return "Je notities: " + ". ".join(regels)


def wikipedia(opdracht):
    gevonden = re.search(
        r"(?:wat is|wat zijn|wie is|wie was|zoek|vertel me over)\s+(?:een |de |het )?(.+)",
        opdracht,
    )
    if not gevonden:
        return "Waar wil je meer over weten?"
    onderwerp = gevonden.group(1).strip()
    url = "https://nl.wikipedia.org/api/rest_v1/page/summary/" + quote(onderwerp.replace(" ", "_"))
    try:
        antwoord = requests.get(url, headers={"User-Agent": "JarvisSchoolProject/1.0"}, timeout=5)
        if antwoord.status_code != 200:
            return f"Ik vind niets over {onderwerp}."
        zinnen = antwoord.json().get("extract", "").split(". ")
        return ". ".join(zinnen[:2]).strip() or f"Ik vind niets over {onderwerp}."
    except (requests.RequestException, ValueError):
        return "Ik kan Wikipedia nu niet bereiken. Heb je internet?"

COMMANDOS = [
    (["hoe laat", "tijd"], tijd),
    (["datum", "welke dag", "hoeveel dag"], datum),
    (["weer", "temperatuur", "regen"], weer),
    (["reken"], rekenen),
    (["notities", "onthouden heb"], notities_lezen),
    (["onthoud"], notitie_opslaan),
    (["open", "ga naar"], open_website),
    (["grap", "mop"], grap),
    (["wie ben jij", "hoe heet jij", "wat ben jij"], naam),
    (["hallo", "hoi", "goedemorgen", "goedemiddag"], begroeting),
    (["wat is", "wat zijn", "wie is", "wie was", "zoek", "vertel me over"], wikipedia),
]


def verwerk(opdracht):
    """Zoek het eerste commando waarvan een trefwoord in de opdracht zit."""
    opdracht = opdracht.lower()
    for woorden, functie in COMMANDOS:
        if any(woord in opdracht for woord in woorden):
            return functie(opdracht)
    return "Dat snap ik niet. Probeer: tijd, datum, weer, grap, reken 5 plus 3 of open youtube."