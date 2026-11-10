import subprocess

VOICE_ENABLED = True

def speak_reply(text):
    if not VOICE_ENABLED:
        return

    try:
        subprocess.Popen(
            ["termux-tts-speak", str(text)]
        )
    except Exception as e:
        print("VOICE ERROR:", e)

if __name__ == "__main__":
    speak_reply(
        "Hello! I am VERNTY ONE. Voice system activated."
    )
