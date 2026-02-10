import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re

# Paths
MODEL_PATH = "fake_news_model.h5"
TOKENIZER_PATH = "tokenizer.pkl"
MAX_LENGTH = 200

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def main():
    print("\n===========================================")
    print("      FAKE NEWS DETECTOR AI APP           ")
    print("===========================================")
    
    # Check artifacts
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TOKENIZER_PATH):
        print("[ERROR] Model files not found!")
        print("Please run 'python train.py' first to build the AI.")
        return

    print("Loading AI Model... please wait...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        with open(TOKENIZER_PATH, 'rb') as handle:
            tokenizer = pickle.load(handle)
        print("[SUCCESS] System Ready!")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return

    # User Input Loop
    print("\n-------------------------------------------")
    print("Type a news headline below to verify it.")
    print("Type 'exit' to close the app.")
    print("-------------------------------------------")

    while True:
        try:
            user_input = input("\n>> News Headline: ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue

            # Preprocess
            cleaned = clean_text(user_input)
            seq = tokenizer.texts_to_sequences([cleaned])
            padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post', truncating='post')
            
            # Predict
            prediction = model.predict(padded, verbose=0)[0][0]
            
            # Result
            is_real = prediction > 0.5
            confidence = prediction if is_real else 1 - prediction
            label = "REAL NEWS" if is_real else "FAKE NEWS"
            
            print(f"   [RESULT]: {label}")
            print(f"   [CONFIDENCE]: {confidence*100:.2f}%")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error processing text: {e}")

if __name__ == "__main__":
    main()
