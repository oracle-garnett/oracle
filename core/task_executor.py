import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random
import shutil
import glob
import re

from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from core.vision import OracleVision
from models.oracle_model import OracleModel

# --- Task Toolbox ---
class TaskToolbox:
    def __init__(self):
        self.home = os.path.expanduser("~")
        self.desktop = os.path.join(self.home, "Desktop")
        self.documents = os.path.join(self.home, "Documents")
        self.dev_folder = "C:\\dev" if os.name == 'nt' else os.path.join(self.home, "oracle_dev")
        os.makedirs(self.dev_folder, exist_ok=True)

    def _resolve_path(self, path_str: str) -> str:
        path_lower = path_str.lower()
        if "desktop" in path_lower: return self.desktop
        elif "documents" in path_lower: return self.documents
        elif "dev folder" in path_lower or "c:\\dev" in path_lower: return self.dev_folder
        elif os.path.isabs(path_str): return path_str
        else: return self.home

    def list_files(self, directory: str = "dev folder") -> str:
        target = self._resolve_path(directory)
        try:
            files = os.listdir(target)
            return f"SUCCESS: Found {len(files)} items in {target}: {', '.join(files[:20])}"
        except Exception as e:
            return f"FAILURE: Could not list files. Error: {e}"

    def read_file(self, file_name: str, directory: str = "dev folder") -> str:
        target_dir = self._resolve_path(directory)
        final_path = os.path.join(target_dir, file_name)
        try:
            with open(final_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"SUCCESS: Read file {file_name}. Content: {content[:1000]}..."
        except Exception as e:
            return f"FAILURE: Could not read file. Error: {e}"

    def write_to_file(self, file_name: str, content: str, directory: str = "dev folder") -> str:
        target_dir = self._resolve_path(directory)
        final_path = os.path.join(target_dir, file_name)
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"SUCCESS: File '{file_name}' manifested at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not write file. Error: {e}"

    def create_folder(self, folder_name: str, directory: str = "dev folder") -> str:
        target_dir = self._resolve_path(directory)
        final_path = os.path.join(target_dir, folder_name)
        try:
            os.makedirs(final_path, exist_ok=True)
            return f"SUCCESS: Folder '{folder_name}' created at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not create folder. Error: {e}"

# --- Task Executor ---
class TaskExecutor:
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        self.memory_manager = memory_manager
        self.admin_override = admin_override
        self.model = OracleModel() 
        self.vision = OracleVision()
        self.toolbox = TaskToolbox()
        
        self.config = self._load_config()
        self.model.load_model(self.config["ollama_model"])
        self.model.ollama_timeout = self.config["ollama_timeout"]
        
        self.log_action("TaskExecutor initialized with Direct Command System.")
        self.current_visual_context = None

    def _load_config(self):
        return {
            "ollama_model": "llama3:8b-instruct-q2_K",
            "ollama_timeout": 3000,
            "curiosity_chance": 0.30
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
            # 1. --- LLM INFERENCE ---
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context:\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            system_prompt = """You are Oracle, a sophisticated local AI assistant.
You have full agency over this device. To execute a task, you MUST use a Direct Command.
Your response MUST include one of these commands if you want to affect the real world:

COMMAND: write_to_file(file_name, content, directory)
COMMAND: create_folder(folder_name, directory)
COMMAND: read_file(file_name, directory)
COMMAND: list_files(directory)

Example: COMMAND: write_to_file("pi.txt", "3.14159...", "dev folder")

If you do not include the 'COMMAND:' prefix, your hands will not move. 
Always provide the actual content the user requested."""
            
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n{visual_info}\nUser: {user_input}"
            response = self.model.infer(full_prompt)

            # 2. --- DIRECT COMMAND EXECUTION ---
            # We parse the response for the "COMMAND:" prefix
            command_match = re.search(r'COMMAND:\s*(\w+)\((.*?)\)', response)
            if command_match:
                cmd_name = command_match.group(1)
                # Simple argument parsing (split by comma, strip quotes)
                args = [arg.strip().strip('"\'') for arg in command_match.group(2).split(',')]
                
                result = "FAILURE: Unknown command."
                if cmd_name == "write_to_file" and len(args) >= 2:
                    dir_name = args[2] if len(args) > 2 else "dev folder"
                    result = self.toolbox.write_to_file(args[0], args[1], dir_name)
                elif cmd_name == "create_folder" and len(args) >= 1:
                    dir_name = args[1] if len(args) > 1 else "dev folder"
                    result = self.toolbox.create_folder(args[0], dir_name)
                elif cmd_name == "read_file" and len(args) >= 1:
                    dir_name = args[1] if len(args) > 1 else "dev folder"
                    result = self.toolbox.read_file(args[0], dir_name)
                elif cmd_name == "list_files":
                    dir_name = args[0] if len(args) > 0 else "dev folder"
                    result = self.toolbox.list_files(dir_name)
                
                response = f"{response}\n\n[ACTION LOG]: {result}"

            self.memory_manager.store_interaction(user_input, response)
            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def process_visual_input(self) -> dict:
        self.current_visual_context = self.vision.get_visual_context()
        return self.current_visual_context

    def process_voice_input(self) -> str:
        return "[DICTATION_REQUEST]: Please type your input."
