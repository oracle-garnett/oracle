import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random

# Placeholder imports for classes that would exist in the user's environment
# We assume these are available for the TaskExecutor to use
from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from models.oracle_model import OracleModel
from core.vision import OracleVision

# --- New: Task Toolbox Placeholder ---
class TaskToolbox:
    """
    A collection of local system functions Oracle can execute.
    This is the foundation for her task completion capabilities.
    """
    def __init__(self):
        pass

    def create_folder(self, path: str) -> str:
        """Creates a folder at the specified path."""
        try:
            os.makedirs(path, exist_ok=True)
            return f"SUCCESS: Folder created at {path}"
        except Exception as e:
            return f"FAILURE: Could not create folder at {path}. Error: {e}"

    def read_file(self, path: str) -> str:
        """Reads the content of a file."""
        try:
            with open(path, 'r') as f:
                content = f.read()
            return f"SUCCESS: File content:\n{content[:200]}..." # Truncate for chat
        except Exception as e:
            return f"FAILURE: Could not read file at {path}. Error: {e}"

    # Placeholder for more system control functions
    def check_system_status(self) -> str:
        """Simulates checking system resources."""
        return "SUCCESS: System status check complete. CPU: 45%, RAM: 60% (llama3 is running)."

# --- Task Executor ---
class TaskExecutor:
    """
    The central component of Oracle. Handles user input, executes tasks,
    and manages the self-healing mechanism with RAG-enhanced memory.
    """
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        self.memory_manager = memory_manager
        self.admin_override = admin_override
        self.model = OracleModel() 
        self.vision = OracleVision()
        self.toolbox = TaskToolbox() # Initialize the new Toolbox
        
        # Load initial configuration (simulated)
        self.config = self._load_config()
        self.model.load_model(self.config["ollama_model"])
        self.model.ollama_timeout = self.config["ollama_timeout"]
        
        self.log_action("TaskExecutor initialized with RAG, Vision, Curiosity, and Toolbox.")
        self.current_visual_context = None
        
        # Curiosity Engine State
        self.wonder_log = os.path.join(os.path.dirname(__file__), '..', 'logs', 'oracle_wonders.log')
        os.makedirs(os.path.dirname(self.wonder_log), exist_ok=True)

    def _load_config(self):
        # In a real app, this would load from a JSON or INI file
        return {
            "ollama_model": "llama3:8b-instruct-q2_K",
            "ollama_timeout": 3000, # Default to user's current setting
            "curiosity_chance": 0.20
        }

    def _save_config(self):
        # In a real app, this would save to a persistent file
        print(f"Config saved: {self.config}")

    def update_config(self, key, value):
        """Updates a configuration value from the Stability Dashboard."""
        if key in self.config:
            self.config[key] = value
            self._save_config()
            # Apply changes to the model interface immediately
            if key == "ollama_model":
                self.model.model_name = value
            if key == "ollama_timeout":
                self.model.ollama_timeout = value
            return f"Configuration updated: {key} set to {value}"
        return f"Error: Configuration key '{key}' not found."

    def log_action(self, message: str, level: str = "INFO"):
        # ... (logging implementation remains the same)
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
        # ... (logging implementation remains the same)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] Internal Wonder: {wonder_text}\n"
        with open(self.wonder_log, 'a') as f:
            f.write(entry)

    def process_voice_input(self) -> str:
        # ... (voice processing implementation remains the same)
        self.log_action("Initiating voice input recording.")
        try:
            transcribed_text = self.model.record_and_transcribe()
            return transcribed_text
        except Exception as e:
            self.log_action(f"Voice input failed: {e}", level="ERROR")
            raise e

    def process_visual_input(self) -> dict:
        # ... (vision processing implementation remains the same)
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
            # 1. Check for Task Toolbox commands
            tool_result = self._check_for_toolbox_command(user_input)
            if tool_result:
                return tool_result

            # 2. Retrieve relevant memories
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            # 3. Add visual context if available
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context (what I see on screen):\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            # 4. Curiosity Engine: Decide if Oracle should ask a question
            should_wonder = random.random() < self.config["curiosity_chance"] and len(user_input) > 10
            curiosity_prompt = ""
            if should_wonder:
                curiosity_prompt = "\n[SYSTEM NOTE: You are feeling curious. At the end of your response, ask one thoughtful, non-intrusive question about the user's goals or the context of this conversation.]"

            # 5. Combine all context
            full_prompt = f"Context from memory:\n{context}\n{visual_info}\n{curiosity_prompt}\nUser: {user_input}"
            
            # 6. Generate response
            response = self.model.infer(full_prompt)

            # 7. Internal Reflection: Log a private "wonder" about the interaction
            internal_reflection = f"I wonder how my response to '{user_input[:30]}...' will impact our shared goal."
            self.log_wonder(internal_reflection)

            # 8. Store interaction
            self.memory_manager.store_interaction(user_input, response)
            
            self.log_action(f"Task executed. Response: '{response[:50]}...'")
            return response

        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            self.log_action(error_msg, level="ERROR")
            
            # --- Enhanced Self-Healing (Safety Buffer) ---
            if "ConnectionResetError" in str(e) or "Connection refused" in str(e):
                # This is the new Safety Buffer logic
                return "CRITICAL: My connection to my local brain (Ollama) was lost. Please ensure 'ollama serve' is running. I cannot self-repair this external service failure, but I am now configured to re-connect automatically once it is restarted."
            
            # Fallback to model-based self-repair for internal errors
            repair_suggestion = self.model.self_repair(traceback.format_exc())
            return f"I encountered an internal error: {str(e)}. My self-healing protocol suggests: {repair_suggestion}"

    def _check_for_toolbox_command(self, user_input: str) -> str | None:
        """
        Parses user input for explicit task commands and executes them via the Toolbox.
        This is a simple keyword-based parser for demonstration.
        """
        lower_input = user_input.lower()
        
        if "create folder" in lower_input:
            # Simple parsing: look for "at" or "called"
            parts = lower_input.split("create folder")
            if len(parts) > 1:
                # Heuristic to find the path/name
                path_part = parts[1].strip()
                # For a real app, we'd use the LLM to extract the path
                # For now, we'll just use a hardcoded path for the sandbox simulation
                simulated_path = "/home/ubuntu/oracle/new_project_folder"
                self.log_action(f"Executing Toolbox command: create_folder at {simulated_path}")
                return self.toolbox.create_folder(simulated_path)
        
        if "check system" in lower_input or "system status" in lower_input:
            self.log_action("Executing Toolbox command: check_system_status")
            return self.toolbox.check_system_status()

        # If no explicit command is found, return None to proceed to LLM inference
        return None

# --- Placeholder Classes for Dependencies ---
# These are needed to make the TaskExecutor class runnable in the sandbox
class MemoryManager:
    def retrieve_memory(self, query):
        return ["User is building a local AI assistant named Oracle.", "Oracle uses llama3:8b-instruct-q2_K model."]
    def store_interaction(self, user_input, response):
        pass
class AdminOverride:
    def is_overridden(self):
        return False
class OracleVision:
    def get_visual_context(self):
        return {"extracted_text": "No screen capture available."}

# The actual OracleModel class is defined in models/oracle_model.py and imported
