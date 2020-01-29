from app import app
from flask_login import current_user
import pyaudio
import os
from pydub import AudioSegment
import wave
import pickle
from sys import byteorder
from array import array
from struct import pack
from sklearn.neural_network import MLPClassifier
from .utils import extract_feature

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000

SILENCE = 30

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in range(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*RATE))])
    return r


def audio_emotion_analysis(audio_file):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/audio'
    )

    audio = AudioSegment.from_mp3(audio_file)
    audio.export(os.path.join(directory, "sentiment.wav"), format="wav")

    AUDIO_FILE = os.path.join(directory, "sentiment.wav")

    # load the NN Model
    model = pickle.load(open("app/utils/audio_sentiment/mlp_classifier.model", "rb"))

    # extract features and reshape it
    features = extract_feature(AUDIO_FILE, mfcc=True, chroma=True, mel=True).reshape(1, -1)
    # predict
    result = model.predict(features)

    return str(str(result)[2:-2]).capitalize()
