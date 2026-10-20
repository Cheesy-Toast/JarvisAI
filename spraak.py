"""spraak.py - de oren en de mond van Jarvis (Peter).

Twee functies, meer hoeft de rest van het project niet te weten:
    luister()  -> tekst (string) van wat de gebruiker zei
    zeg(tekst) -> spreekt de tekst uit

We nemen op met `sounddevice` (geen Homebrew of PyAudio nodig) en laten Google
de opname omzetten naar tekst. Werkt de microfoon niet? Dan schakelt
luister() automatisch over op typen.
"""
import subprocess
import sys

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import numpy as np
    import sounddevice as sd
except (ImportError, OSError):
    np = None
    sd = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# True = typen in plaats van praten (vangnet als de microfoon niet werkt)
TEKSTMODUS = sr is None or sd is None

SAMPLERATE = 16000       # opnamekwaliteit (16 kHz is genoeg voor spraak)
BLOK = 0.1               # we meten elke 0,1 seconde hoe hard het is
MAX_WACHTEN = 8          # zoveel seconden wachten we tot iemand begint te praten
MAX_SPREKEN = 10         # zoveel seconden mag iemand praten
STILTE_EINDE = 1.0       # zoveel seconden stilte = de zin is af

_herkenner = sr.Recognizer() if sr else None
_engine = None


def zeg(tekst):
    """Print het antwoord en spreek het uit."""
    global _engine
    print("Jarvis:", tekst)

    if sys.platform == "darwin":
        # Mac: de ingebouwde stem, dus geen extra installatie nodig.
        # We proberen eerst een Nederlandse stem en vallen anders terug op de standaard.
        resultaat = subprocess.run(["say", "-v", "Xander", tekst], capture_output=True)
        if resultaat.returncode != 0:
            subprocess.run(["say", tekst], capture_output=True)
        return

    if pyttsx3 is None:
        return
    if _engine is None:
        _engine = pyttsx3.init()
    _engine.say(tekst)
    _engine.runAndWait()


def _volume(blok):
    """Hoe hard is dit stukje geluid?"""
    return float(np.sqrt(np.mean(blok.astype(np.float32) ** 2)))


def _neem_op():
    """Neem op tot de gebruiker klaar is met praten. Geeft None als niemand praat."""
    blokgrootte = int(SAMPLERATE * BLOK)
    blokken = []
    vorige = None
    gesproken = False
    stilte = 0.0
    tijd = 0.0

    with sd.InputStream(samplerate=SAMPLERATE, channels=1, dtype="int16") as stroom:
        # Eerst een halve seconde omgevingsgeluid meten, zodat we weten wat "stil" is.
        ruis = [_volume(stroom.read(blokgrootte)[0][:, 0]) for _ in range(5)]
        drempel = max(300.0, 3 * (sum(ruis) / len(ruis)))

        while True:
            blok = stroom.read(blokgrootte)[0][:, 0]
            tijd += BLOK

            if _volume(blok) > drempel:
                if not gesproken and vorige is not None:
                    blokken.append(vorige)  # het begin van de zin niet kwijtraken
                gesproken = True
                stilte = 0.0
            elif gesproken:
                stilte += BLOK

            if gesproken:
                blokken.append(blok)
            vorige = blok

            if not gesproken and tijd >= MAX_WACHTEN:
                return None
            if gesproken and (stilte >= STILTE_EINDE or tijd >= MAX_WACHTEN + MAX_SPREKEN):
                break

    return np.concatenate(blokken).tobytes()


def luister():
    """Luister via de microfoon. Geeft een lege string als er niets verstaan is."""
    global TEKSTMODUS

    if not TEKSTMODUS:
        try:
            print("[luisteren...]")
            opname = _neem_op()
            if opname is None:
                return ""
            audio = sr.AudioData(opname, SAMPLERATE, 2)
            tekst = _herkenner.recognize_google(audio, language="nl-NL").lower()
            print("Jij:", tekst)
            return tekst
        except sr.UnknownValueError:
            return ""  # niet verstaan: gewoon opnieuw proberen
        except sr.RequestError:
            print("Geen internet voor spraakherkenning. Ik schakel over op typen.")
            TEKSTMODUS = True
        except (OSError, sd.PortAudioError):
            print("De microfoon werkt niet. Ik schakel over op typen.")
            TEKSTMODUS = True

    return input("Jij: ").lower().strip()