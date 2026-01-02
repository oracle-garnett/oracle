import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time

from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from models.oracle_model import OracleModel

class TaskExecutor:
    """
    The central component of Oracle. Handles user input, executes tasks,
    and manages the self-healing mechanism with RAG-enhanced memory.
    """
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        self.memory_manager = memory_manager
        self.admin_override = admin_override
        self.model = OracleModel() 
        self.model.load_model("ollama-local") # Connect to local Ollama
        self.log_action("TaskExecutor initialized with RAG support.")

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

    def process_voice_input(self) -> str:
        """Handles the recording and transcription of voice input."""
        self.log_action("Initiating voice input recording.")
        try:
            # This calls the Whisper model in the OracleModel class
            transcribed_text = self.model.record_and_transcribe()
            return transcribed_text
        except Exception as e:
            self.log_action(f"Voice input failed: {e}", level="ERROR")
            raise e

    def execute_task(self, user_input: str) -> str:
        """Processes user input with context from RAG memory."""
        self.log_action(f"Received user input: '{user_input}'")

        if self.admin_override.is_overridden():
            return "System is currently under administrative override."

        try:
            # 1. Retrieve relevant memories using RAG
            relevant_memories = self.memory_manager.retrieve_memory(user_input)
            
            # 2. Build prompt with context
            prompt = self._build_prompt(user_input, relevant_memories)
            
            # 3. Generate response
            response = self.model.infer(prompt)

            # 4. Store interaction in RAG and encrypted logs
            self.memory_manager.store_interaction(user_input, response)
            
            self.log_action(f"Task executed. Response: '{response[:50]}...'")
            return response

        except Exception as e:
            self.log_action(f"Task execution failed: {e}", level="ERROR")
            return self.self_heal(e)

    def _build_prompt(self, user_input: str, memories: List[str]) -> str:
        """Constructs the prompt with RAG context."""
        context = "\n".join([f"- {m}" for m in memories])
        
        system_prompt = (
            "You are Oracle, an evolving, highly intelligent AI assistant. "
            "You remember past interactions and grow more powerful over time. "
            "Use the provided context to inform your response. Be concise and autonomous."
        )
        
        full_prompt = f"{system_prompt}\n\n--- RELEVANT MEMORIES ---\n{context}\n\n--- NEW REQUEST ---\nUser: {user_input}\nOracle:"
        return full_prompt

    def self_heal(self, error: Exception) -> str:
        """Attempts to fix the code or configuration."""
        error_details = traceback.format_exc()
        self.log_action(f"Self-healing initiated: {error_details}", level="CRITICAL")
        fix_suggestion = self.model.self_repair(error_details)
        
        if "FIX_SUCCESS" in fix_suggestion:
            return "An internal error occurred, but I have successfully self-corrected. Please try again."
        
        return f"Critical error encountered. Self-correction failed. Error: {type(error).__name__}"
