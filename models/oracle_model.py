"""
Oracle Model Interface

This module will contain the integration with various AI models, including local LLMs (via Ollama),
Whisper for STT, and pyttsx3 for TTS.
"""
import time
import random
import os

class OracleModel:
    """
    The "brain" of Oracle. This class will interface with the selected AI model(s).
    """
    def __init__(self):
        self.model_name = None
        self.is_loaded = False

    def load_model(self, model_name: str):
        """Loads the specified AI model (placeholder for Ollama/Whisper)."""
        self.model_name = model_name
        self.is_loaded = True
        print(f"Model '{model_name}' interface loaded. (Actual model loading with Ollama/Whisper is a user-side setup step.)")

    def infer(self, prompt: str) -> str:
        """
        Generates a response using the local Ollama server.
        """
        import requests
        import json

        if not self.is_loaded:
            return "Model not loaded. Please initialize the model first."

        try:
            # Connect to local Ollama server
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral", # Default to mistral, can be changed to llama3
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "I received an empty response from the model.")
            else:
                return f"Error from Ollama: {response.status_code}. Make sure 'ollama serve' is running."
        
        except Exception as e:
            # Fallback to a helpful message if Ollama isn't reachable
            return f"I couldn't reach my local brain (Ollama). Error: {str(e)}. Please ensure 'ollama serve' is running in your terminal."

    def self_repair(self, error_details: str) -> str:
        """
        Uses the model to generate a fix for the given error.
        This is the core of Oracle's self-healing capability.
        """
        # In a real scenario, this would call the LLM with the error details
        # For now, we simulate a fix suggestion
        if "ZeroDivisionError" in error_details:
            return "FIX_SUCCESS: Apply patch to core/math_utils.py to check for zero before division."
        
        return "FIX_FAILURE: Error is too complex for current self-repair model. Manual intervention required."

    def record_and_transcribe(self, duration: int = 5) -> str:
        """
        Records audio from the microphone and transcribes it using Whisper.
        """
        import whisper
        import sounddevice as sd
        import scipy.io.wavfile as wav
        import numpy as np

        # 1. Load the Whisper model (will download on first run)
        model = whisper.load_model("base")

        # 2. Record audio
        fs = 44100  # Sample rate
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        
        # 3. Save to temporary file
        temp_filename = "temp_voice.wav"
        wav.write(temp_filename, fs, recording)

        # 4. Transcribe
        result = model.transcribe(temp_filename)
        os.remove(temp_filename) # Clean up
        
        return result["text"].strip()

    def text_to_speech(self, text: str):
        """
        Converts text to speech using pyttsx3.
        """
        # In a real scenario, this would call pyttsx3
        print(f"Speaking: '{text}'")
        # import pyttsx3
        # engine = pyttsx3.init()
        # engine.say(text)
        # engine.runAndWait()
        pass
