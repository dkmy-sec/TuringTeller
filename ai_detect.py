# ai_detect.py
import os
import openai
import torch
import requests


openai.api_key = os.getenv("OPENAI_API_KEY")

def detect_ai_text(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Determine if the following text was written by an AI or a human:\n\n{text}\n\nAnswer with 'AI-generated' or 'Human-generated'.",
            max_tokens=1,
            n=1,
            stop=None,
            temperature=0
        )
        result = response.choices[0].text.strip()
        return result == 'AI-generated'
    except Exception as e:
        print(f"Error during AI detection: {e}")
        return False

def analyze_audio_file(filepath):
    try:
        from speechbrain.inference import EncoderClassifier

        # Load the pre-trained anti-spoofing model
        model = EncoderClassifier.from_hparams(
            source="MattyB95/AST-ASVspoof5-Synthetic-Voice-Detection",
            savedir="pretrained_models/AST-ASVspoof5-Synthetic-Voice-Detection",
            use_auth_token=os.getenv("HUGGINGFACE_HUB_TOKEN")
        )

        # Perform inference using the classify_file method
        prediction = model.classify_file(filepath)
        predicted_label = prediction[0]
        print(f"Predicted label: {predicted_label}")

        # Determine if the audio is AI-generated
        is_ai_generated = predicted_label == 'spoof'
        return is_ai_generated
    except Exception as e:
        print(f"Error analyzing audio file: {e}")
        return False

def analyze_video_file(filepath):
    api_key = 'your_deepware_api_key'
    url = 'https://api.deepware.ai/analyze'
    files = {'file':open(filepath, 'rb')}
    headers = {'Authorization': f'Bearer {api_key}'}

    response = requests.post(url, files=files, headers=headers)
    result = response.json()

    # Parse the response
    is_ai_generated = result.get('deepfake', False)
    return is_ai_generated


def analyze_media(filepath):
    extension = os.path.splitext(filepath)[1].lower()
    if extension in ['.mp3', '.wav']:
        return analyze_audio_file(filepath)
    elif extension in ['.mp4', '.mov']:
        return analyze_video_file(filepath)
    else:
        raise ValueError("Unsupported file type")


def process_media_file(filepath):
    try:
        is_ai_generated = analyze_media(filepath)
        result = "AI-generated" if is_ai_generated else "Human-generated"
    except Exception as e:
        print(f"Error processing media file: {e}")
        result = "Error processing file. Please try again."
    return result