import speech_recognition as sr
import os
from pydub import AudioSegment
from app import app
from flask_login import current_user

def transcribe_audio_to_text(audio_file):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/audio'
    )

    audio = AudioSegment.from_mp3(audio_file)
    audio.export(os.path.join(directory, "audio.wav"), format="wav")

    AUDIO_FILE = os.path.join(directory, "audio.wav")

    r = sr.Recognizer()

    with sr.AudioFile(AUDIO_FILE) as source:
        r.adjust_for_ambient_noise(source)
        audio = r.record(source)  # read the entire audio file

    try:
        prediction = r.recognize_google(audio)

        if os.path.exists(os.path.join(directory, "audio.wav")):
                os.remove(os.path.join(directory, "audio.wav"))
        else:
            print("The file does not exist")

        return prediction

    except Exception:   # speech is unintelligible
        return "Could not understand audio"