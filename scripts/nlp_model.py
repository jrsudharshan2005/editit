import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
import numpy as np
import tensorflow as tf


def interpret_command(command):
    sequence = tokenizer.texts_to_sequences([command])
    padded_sequence = pad_sequences(sequence, padding='post')
    prediction = model.predict(padded_sequence)
    effect = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    return effect

data = {
    'command': [
        "increase brightness",
        "decrease brightness",
        "apply grayscale",
        "apply colour",
        "back",
        "front",
        "play at a specific time",
        "pause at a specific time",
        "save the video",
        "export the video"
    ],
    'effect': [
        "increase brightness",
        "decrease brightness",
        "apply grayscale",
        "apply colour",
        "back",
        "front",
        "play at a specific time",
        "pause at a specific time",
        "save the video",
        "export the video"
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Encode labels
label_encoder = LabelEncoder()
df['encoded_effect'] = label_encoder.fit_transform(df['effect'])

# Tokenize commands
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['command'])
sequences = tokenizer.texts_to_sequences(df['command'])
padded_sequences = pad_sequences(sequences, padding='post')

# Define model
model = Sequential([
    Embedding(input_dim=1000, output_dim=64, input_length=padded_sequences.shape[1]),
    GlobalAveragePooling1D(),
    Dense(64, activation='relu'),
    Dense(len(label_encoder.classes_), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Train model
model.fit(padded_sequences, df['encoded_effect'], epochs=10)

# Save model
model.save(r'C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\models\nlp_model.keras')

# Function for interpreting command
def interpret_command(command):
    sequence = tokenizer.texts_to_sequences([command])
    padded_sequence = pad_sequences(sequence, padding='post')
    prediction = model.predict(padded_sequence)
    effect = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    return effect
