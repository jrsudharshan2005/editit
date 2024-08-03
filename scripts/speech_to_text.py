import wave
import json
from vosk import Model, KaldiRecognizer

# Load the Vosk model (replace with the path to your downloaded model)
model = Model(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\models\nlp_model.keras")

def transcribe_audio(audio_path):
    # Open your audio file
    wf = wave.open(audio_path, "rb")

    # Ensure the audio file has the correct parameters (e.g., 16kHz, mono)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Audio file must be WAV format mono PCM at 16kHz")

    # Initialize the recognizer
    rec = KaldiRecognizer(model, wf.getframerate())

    # Process the audio file and accumulate results
    transcript = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            transcript += json.loads(result)['text'] + " "

    # Get the final part of the transcription
    final_result = rec.FinalResult()
    transcript += json.loads(final_result)['text']
    
    return transcript.strip()

def transcribe_realtime(audio_content):
    # Assume the audio content is already in the required format (16kHz, mono)
    rec = KaldiRecognizer(model, 16000)

    # Recognize the audio content
    transcript = ""
    rec.AcceptWaveform(audio_content)
    transcript += json.loads(rec.Result())['text']

    # Get the final part of the transcription
    final_result = rec.FinalResult()
    transcript += json.loads(final_result)['text']

    return transcript.strip()
