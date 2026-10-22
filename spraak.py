"""spraak.py - de oren en de mond van Jarvis (Peter).

Twee functies, meer hoeft de rest van het project niet te weten:
    luister()  -> tekst (string) van wat de gebruiker zei
    zeg(tekst) -> spreekt de tekst uit

Werkt de microfoon niet? Dan schakelt luister() automatisch over op typen.
"""
import subprocess
import sys

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# True = typen in plaats van praten (vangnet als de microfoon niet werkt)
TEKSTMODUS = sr is None

_herkenner = sr.Recognizer() if sr else None
_engine = None


def zeg(tekst):
    """Print het antwoord en spreek het uit."""
    global _engine
    print("Jarvis:", tekst)

    if sys.platform == "darwin":
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


def luister():
    """Luister via de microfoon. Geeft een lege string als er niets verstaan is."""
    global TEKSTMODUS

    if not TEKSTMODUS:
        try:
            with sr.Microphone() as bron:
                print("[luisteren...]")
                _herkenner.adjust_for_ambient_noise(bron, duration=0.5)
                audio = _herkenner.listen(bron, timeout=8, phrase_time_limit=10)
            tekst = _herkenner.recognize_google(audio, language="nl-NL").lower()
            print("Jij:", tekst)
            return tekst
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""  # niets gehoord of niet verstaan: gewoon opnieuw proberen
        except sr.RequestError:
            print("Geen internet voor spraakherkenning. Ik schakel over op typen.")
            TEKSTMODUS = True
        except (OSError, AttributeError):
            print("Microfoon of PyAudio werkt niet. Ik schakel over op typen.")
            TEKSTMODUS = True

    return input("Jij: ").lower().strip()