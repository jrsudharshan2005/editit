import os
import cv2
import threading
import queue
import pyaudio
import wave
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import LabelEncoder
from Scripts.speech_to_text import transcribe_realtime
from Scripts.nlp_model import interpret_command
from Scripts.video_effects import apply_grayscale, apply_colour, adjust_brightness

# Load the trained NLP model
nlp_model = tf.keras.models.load_model(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\models\nlp_model.keras")
nlp_model = tf.keras.models.load_model(nlp_model_path)
label_encoder = LabelEncoder()
label_encoder.classes_ = ['apply colour', 'apply grayscale', 'decrease brightness', 'front', 'increase brightness', 'pause at a specific time', 'play at a specific time', 'save the video', 'export the video', 'back']

# Real-time video processing
def process_frame(frame, effect):
    if effect == 'apply grayscale':
        return apply_grayscale(frame)
    elif effect == 'apply colour':
        return apply_colour(frame)
    elif effect == 'increase brightness':
        return adjust_brightness(frame, 30)
    elif effect == 'decrease brightness':
        return adjust_brightness(frame, -30)
    else:
        return frame

# Real-time audio processing
def capture_audio(audio_queue, stop_event):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    WAVE_OUTPUT_FILENAME = os.path.join("..", "data", "audio_commands", "realtime_command.wav")

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(WAVE_OUTPUT_FILENAME), exist_ok=True)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("* recording")
    frames = []

    while not stop_event.is_set():
        data = stream.read(CHUNK)
        frames.append(data)

        # Save the frames to a WAV file every few seconds to transcribe
        if len(frames) >= RATE // CHUNK * 1:  # Transcribe every second
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            # Transcribe and interpret command
            with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
                audio_content = audio_file.read()
            command_text = transcribe_realtime(audio_content)
            effect = interpret_command(command_text)
            if effect:
                audio_queue.put(effect)
            frames = []  # Reset frames for next transcription

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("* done recording")

# Real-time video editing
def realtime_video_editing(video_path):
    cap = cv2.VideoCapture(video_path)
    audio_queue = queue.Queue()
    effect = None
    stop_event = threading.Event()

    audio_thread = threading.Thread(target=capture_audio, args=(audio_queue, stop_event))
    audio_thread.start()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Check if there is a new effect
        if not audio_queue.empty():
            effect = audio_queue.get()

        # Process the video frame
        if effect:
            frame = process_frame(frame, effect)

        # Display the video frame
        cv2.imshow('frame', frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stop_event.set()
    audio_thread.join()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = os.path.join('..', 'data', 'videos', 'input_video.mp4')
    realtime_video_editing(video_path)
