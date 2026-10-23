import speech_recognition as sr

recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Listening...")

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

            print("Recognizing...")
            text = recognizer.recognize_google(audio)

            return text

        except sr.WaitTimeoutError:
            return "You didn't say anything."

        except sr.UnknownValueError:
            return "I heard you, but couldn't understand what you said."

        except sr.RequestError as e:
            return f"Google Speech Recognition error: {e}"


while True:
    text = listen()
    print("You said:", text)