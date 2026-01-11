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
        
        self.log_action("TaskExecutor initialized with Robust Action Logic.")
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
            # 1. --- ROBUST INTENT PARSING ---
            # We check for intent before the LLM even speaks to ensure the "Hands" move.
            tool_result, tool_used = self._robust_parser(user_input)
            
            # 2. --- LLM INFERENCE ---
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context:\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            # We tell the LLM if the tool was already triggered
            action_status = f"\n[SYSTEM STATUS]: {tool_result}" if tool_used else ""
            
            system_prompt = """You are Oracle, a sophisticated local AI assistant.
You have full agency over this device. You are NOT a chatbot; you are an integrated agent.
If the user asks for an action, the system will attempt to trigger your 'Hands' automatically.
Your job is to confirm the action and provide the intelligent response the user expects."""
            
            full_prompt = f"{system_prompt}\n\n{action_status}\n\nContext:\n{context}\n{visual_info}\nUser: {user_input}"
            response = self.model.infer(full_prompt)

            # 3. --- POST-RESPONSE VERIFICATION ---
            # If the LLM says she did something but the tool wasn't used, we try one last time.
            if not tool_used:
                tool_result, tool_used = self._robust_parser(response)
                if tool_used:
                    response = f"{response}\n\n[ACTION VERIFIED]: {tool_result}"

            self.memory_manager.store_interaction(user_input, response)
            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def _robust_parser(self, text: str) -> (str | None, bool):
        """Uses regex and intent matching to ensure tools are triggered."""
        lower_text = text.lower()
        
        # --- FILE WRITING (The most common failure) ---
        # Matches: "save pi to pi.txt", "write 'hello' to file", "create file called test.txt with content..."
        write_match = re.search(r'(?:save|write|create|put)\s+(.*?)\s+(?:to|in|into)\s+(?:file|called|a file)\s+([a-zA-Z0-9_\-\.]+)', lower_text)
        if not write_match:
            # Alternative: "create a file called test.txt with content..."
            write_match = re.search(r'(?:create|make)\s+(?:a\s+)?file\s+called\s+([a-zA-Z0-9_\-\.]+)\s+(?:with|containing)\s+(.*)', lower_text)
        
        if write_match:
            # Handle different match groups based on the regex that hit
            if "called" in write_match.group(0):
                file_name = write_match.group(1)
                content = write_match.group(2) if len(write_match.groups()) > 1 else "Generated by Oracle."
            else:
                content = write_match.group(1)
                file_name = write_match.group(2)
            
            directory = "desktop" if "desktop" in lower_text else "dev folder"
            self.log_action(f"Robust Parser triggered: write_to_file('{file_name}', '{directory}')")
            return self.toolbox.write_to_file(file_name, content, directory), True

        # --- FOLDER CREATION ---
        folder_match = re.search(r'(?:create|make|new)\s+(?:folder|directory)\s+(?:called|named|label it)\s+([a-zA-Z0-9_\-\s]+)', lower_text)
        if folder_match:
            folder_name = folder_match.group(1).strip()
            directory = "desktop" if "desktop" in lower_text else "dev folder"
            self.log_action(f"Robust Parser triggered: create_folder('{folder_name}', '{directory}')")
            return self.toolbox.create_folder(folder_name, directory), True

        # --- FILE READING ---
        read_match = re.search(r'(?:read|get|retrieve|look at)\s+(?:the\s+)?(?:data\s+in\s+)?([a-zA-Z0-9_\-\.]+)', lower_text)
        if read_match:
            file_name = read_match.group(1)
            directory = "desktop" if "desktop" in lower_text else "dev folder"
            self.log_action(f"Robust Parser triggered: read_file('{file_name}', '{directory}')")
            return self.toolbox.read_file(file_name, directory), True

        return None, False

    def process_visual_input(self) -> dict:
        self.current_visual_context = self.vision.get_visual_context()
        return self.current_visual_context

    def process_voice_input(self) -> str:
        return "[DICTATION_REQUEST]: Please type your input."
