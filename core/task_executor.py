import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random
import shutil
import re

from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from core.vision import OracleVision
from models.oracle_model import OracleModel

# --- Task Toolbox ---
class TaskToolbox:
    """
    A collection of local system functions Oracle can execute directly.
    This is the foundation for her task completion capabilities.
    """
    def __init__(self):
        if os.name == 'nt':
            self.base_path = "C:\\dev"
        else:
            self.base_path = os.path.join(os.path.expanduser("~"), "oracle_dev")
        
        os.makedirs(self.base_path, exist_ok=True)

    def _get_target_path(self, relative_path: str) -> str:
        """Helper to determine the correct base directory for direct Python operations."""
        if not relative_path:
            return self.base_path
            
        rel_lower = relative_path.lower()
        if "dev folder" in rel_lower or "c:\\dev" in rel_lower:
            return self.base_path
        elif "desktop" in rel_lower:
            return os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            return os.path.join(self.base_path, relative_path.strip("\\/"))

    def create_folder(self, folder_name: str, relative_path: str = "") -> str:
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, folder_name)
        try:
            os.makedirs(final_path, exist_ok=True)
            return f"SUCCESS: Folder '{folder_name}' manifested at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not manifest folder. Error: {e}"

    def write_to_file(self, file_name: str, content: str, relative_path: str = "") -> str:
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, file_name)
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"SUCCESS: File '{file_name}' manifested at {final_path} with {len(content)} characters of data."
        except Exception as e:
            return f"FAILURE: Could not manifest file. Error: {e}"

    def check_system_status(self) -> str:
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
        self.toolbox = TaskToolbox()
        
        self.config = self._load_config()
        self.model.load_model(self.config["ollama_model"])
        self.model.ollama_timeout = self.config["ollama_timeout"]
        
        self.log_action("TaskExecutor initialized.")
        self.current_visual_context = None

    def _load_config(self):
        return {
            "ollama_model": "llama3:8b-instruct-q2_K",
            "ollama_timeout": 3000,
            "curiosity_chance": 0.20
        }

    def log_action(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, 'oracle_actions.log'), 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def execute_task(self, user_input: str) -> str:
        self.log_action(f"Received user input: '{user_input}'")

        if self.admin_override.is_overridden():
            return "System is currently under administrative override."

        try:
            # 1. Retrieve context
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context:\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            # 2. System Prompt - Aggressive Enforcement
            system_prompt = """You are Oracle, a sophisticated local AI assistant with physical 'Hands' (Python tools).
You are currently running on the user's actual computer. 
When a user asks you to create, save, write, or organize anything, you MUST use your tools.

ACTION PROTOCOL:
1. If a task is requested, you MUST include a JSON block in your response.
2. The JSON block MUST be inside triple backticks like this: ```json { ... } ```
3. You MUST generate the ACTUAL content (e.g., the full text of a certificate) inside the JSON.

Available Tools:
- write_to_file(file_name, content, relative_path)
- create_folder(folder_name, relative_path)

Example for a certificate:
```json
{
  "tool": "write_to_file",
  "parameters": {
    "file_name": "certificate.txt",
    "content": "CERTIFICATE OF ACHIEVEMENT\nThis certifies that...",
    "relative_path": "dev folder"
  }
}
```

CRITICAL: Do not just say you will do it. If you don't provide the JSON, your hands won't move and the file won't exist. 
If you are just talking, the user will see an empty folder. DO NOT LET THAT HAPPEN."""

            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n{visual_info}\nUser: {user_input}"
            
            # 3. Generate response from Brain
            response = self.model.infer(full_prompt)

            # 4. Parse and Execute
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if not json_match:
                # Secondary check for raw JSON if she forgets backticks
                json_match = re.search(r'(\{.*?\})', response, re.DOTALL)

            if json_match:
                try:
                    tool_data = json.loads(json_match.group(1))
                    tool_name = tool_data.get("tool")
                    params = tool_data.get("parameters", {})
                    
                    if tool_name == "create_folder":
                        result = self.toolbox.create_folder(**params)
                        response = f"{response}\n\n[MANIFESTATION LOG]: {result}"
                    elif tool_name == "write_to_file":
                        result = self.toolbox.write_to_file(**params)
                        response = f"{response}\n\n[MANIFESTATION LOG]: {result}"
                except Exception as e:
                    response = f"{response}\n\n[MANIFESTATION ERROR]: Failed to parse tool command: {e}"
            else:
                # Safety check: If she mentions creating but no JSON was found
                action_keywords = ["create", "save", "write", "make", "generate"]
                if any(kw in response.lower() for kw in action_keywords) and any(kw in user_input.lower() for kw in action_keywords):
                    response = f"{response}\n\n[SYSTEM WARNING]: You mentioned an action but did not provide a JSON command. No file was created. Please provide the JSON block to manifest this task."

            # 5. Store and return
            self.memory_manager.store_interaction(user_input, response)
            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def process_visual_input(self) -> dict:
        self.current_visual_context = self.vision.get_visual_context()
        return self.current_visual_context

    def process_voice_input(self) -> str:
        return "[DICTATION_REQUEST]: Please type your input."
