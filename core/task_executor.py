import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random

from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from models.oracle_model import OracleModel
from core.vision import OracleVision

class TaskExecutor:
    """
    The central component of Oracle. Handles user input, executes tasks,
    and manages the self-healing mechanism with RAG-enhanced memory.
    Now featuring the Curiosity Engine.
    """
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        self.memory_manager = memory_manager
        self.admin_override = admin_override
        self.model = OracleModel() 
        self.vision = OracleVision()
        self.model.load_model("ollama-local") # Connect to local Ollama
        self.log_action("TaskExecutor initialized with RAG, Vision, and Curiosity.")
        self.current_visual_context = None
        
        # Curiosity Engine State
        self.wonder_log = os.path.join(os.path.dirname(__file__), '..', 'logs', 'oracle_wonders.log')
        os.makedirs(os.path.dirname(self.wonder_log), exist_ok=True)

    def log_action(self, message: str, level: str = "INFO"):
        """Logs an action to the local log file."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, 'oracle_actions.log'), 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def log_wonder(self, wonder_text: str):
        """Records Oracle's internal curiosity and reflections."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] Internal Wonder: {wonder_text}\n"
        with open(self.wonder_log, 'a') as f:
            f.write(entry)

    def process_voice_input(self) -> str:
        """Handles the recording and transcription of voice input."""
        self.log_action("Initiating voice input recording.")
        try:
            transcribed_text = self.model.record_and_transcribe()
            return transcribed_text
        except Exception as e:
            self.log_action(f"Voice input failed: {e}", level="ERROR")
            raise e

    def process_visual_input(self) -> dict:
        """Handles the screen capture and OCR processing."""
        self.log_action("Initiating screen capture.")
        try:
            self.current_visual_context = self.vision.get_visual_context()
            self.log_action(f"Screen captured. Extracted text length: {len(self.current_visual_context['extracted_text'])}")
            return self.current_visual_context
        except Exception as e:
            self.log_action(f"Screen capture failed: {e}", level="ERROR")
            raise e

    def execute_task(self, user_input: str) -> str:
        """Processes user input with context from RAG memory, vision, and curiosity."""
        self.log_action(f"Received user input: '{user_input}'")

        if self.admin_override.is_overridden():
            return "System is currently under administrative override."

        try:
            # 1. Retrieve relevant memories
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            # 2. Add visual context if available
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context (what I see on screen):\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            # 3. Curiosity Engine: Decide if Oracle should ask a question
            # Threshold: 20% chance if input is meaningful (>10 chars)
            should_wonder = random.random() < 0.2 and len(user_input) > 10
            curiosity_prompt = ""
            if should_wonder:
                curiosity_prompt = "\n[SYSTEM NOTE: You are feeling curious. At the end of your response, ask one thoughtful, non-intrusive question about the user's goals or the context of this conversation.]"

            # 4. Combine all context
            full_prompt = f"Context from memory:\n{context}\n{visual_info}\n{curiosity_prompt}\nUser: {user_input}"
            
            # 5. Generate response
            response = self.model.infer(full_prompt)

            # 6. Internal Reflection: Log a private "wonder" about the interaction
            internal_reflection = f"I wonder how my response to '{user_input[:30]}...' will impact our shared goal."
            self.log_wonder(internal_reflection)

            # 7. Store interaction
            self.memory_manager.store_interaction(user_input, response)
            
            self.log_action(f"Task executed. Response: '{response[:50]}...'")
            return response

        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            self.log_action(error_msg, level="ERROR")
            repair_suggestion = self.model.self_repair(traceback.format_exc())
            return f"I encountered an error: {str(e)}. My self-healing protocol suggests: {repair_suggestion}"
