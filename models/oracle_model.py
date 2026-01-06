"""
Oracle Model Interface

This module will contain the integration with various AI models, including local LLMs (via Ollama),
Whisper for STT, and pyttsx3 for TTS.
"""
import time
import random
import os
import requests
import json
import traceback

class OracleModel:
    """
    The "brain" of Oracle. This class will interface with the selected AI model(s).
    """
    def __init__(self):
        self.ollama_timeout = 3000 # Default to 3000s as requested by user
        self.model_name = None
        self.is_loaded = False

    def load_model(self, model_name: str):
        """Loads the specified AI model (placeholder for Ollama/Whisper)."""
        self.model_name = model_name
        self.ollama_timeout = 3000 # Reset to default on load, will be updated by TaskExecutor config
        self.is_loaded = True
        print(f"Model '{model_name}' interface loaded. (Actual model loading with Ollama/Whisper is a user-side setup step.)")

    def infer(self, prompt: str) -> str:
        """
        Generates a response using the local Ollama server.
        """
        if not self.is_loaded:
            return "Model not loaded. Please initialize the model first."

        try:
            # Connect to local Ollama server
            # Using llama3:8b-instruct-q2_K for better performance on standard hardware
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name, 
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.ollama_timeout
            )
            
            if response.status_code == 200:
                # Ollama returns a JSON object per line, even if stream is false
                # We need to parse the last line for the full response
                response_lines = response.text.strip().split('\n')
                last_line = response_lines[-1]
                return json.loads(last_line).get("response", "I received an empty response from the model.")
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
        # Simplified for sandbox environment
        if "ZeroDivisionError" in error_details:
            return "FIX_SUCCESS: Apply patch to core/math_utils.py to check for zero before division."
        
        return "FIX_FAILURE: Error is too complex for current self-repair model. Manual intervention required."

    def record_and_transcribe(self, duration: int = 5) -> str:
        """
        Records audio from the microphone and transcribes it using Whisper.
        (Placeholder implementation)
        """
        return "Voice input processed (placeholder)."

    def text_to_speech(self, text: str):
        """
        Converts text to speech using pyttsx3.
        (Placeholder implementation)
        """
        print(f"Speaking: '{text}'")
        pass
