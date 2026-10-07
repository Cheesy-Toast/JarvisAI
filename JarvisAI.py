"""jarvis.py - het hoofdprogramma (Douwe). Start Jarvis met:  python3 jarvis.py

Dit bestand knoopt de onderdelen aan elkaar:
    spraak.py  ->  luister() en zeg()      (Peter)
    skills.py  ->  verwerk()               (Ali)
"""
from spraak import luister, zeg
from skills import verwerk

STOPWOORDEN = ["stop", "doei", "tot ziens"]


def main():
    zeg("Hoi, ik ben Jarvis. Waar kan ik mee helpen?")
    while True:
        opdracht = luister()

        if not opdracht:  # niets verstaan: gewoon opnieuw luisteren
            continue

        if any(woord in opdracht for woord in STOPWOORDEN):
            zeg("Doei!")
            break

        zeg(verwerk(opdracht))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Ctrl+C
        print("\nJarvis is gestopt.")