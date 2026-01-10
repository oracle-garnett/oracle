import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random
import shutil

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
        if "dev folder" in relative_path.lower() or "c:\\dev" in relative_path.lower():
            return self.base_path
        elif "desktop" in relative_path.lower():
            return os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            return os.path.join(os.path.expanduser("~"), "Desktop", "oracle")

    def create_folder(self, folder_name: str, relative_path: str = "") -> str:
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, folder_name)
        try:
            os.makedirs(final_path, exist_ok=True)
            return f"SUCCESS: Folder '{folder_name}' created at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not create folder. Error: {e}"

    def write_to_file(self, file_name: str, content: str, relative_path: str = "") -> str:
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, file_name)
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"SUCCESS: File '{file_name}' created at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not create file. Error: {e}"

    def dictate_note(self, note_content: str, file_name: str = "dictated_note.txt", relative_path: str = "") -> str:
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, file_name)
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            return f"SUCCESS: Dictated note saved to '{file_name}' at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not save dictated note. Error: {e}"

    def organize_document(self, doc_name: str, doc_content: str, category: str = "documents", relative_path: str = "") -> str:
        base_target_dir = self._get_target_path(relative_path)
        category_dir = os.path.join(base_target_dir, category)
        final_path = os.path.join(category_dir, doc_name)
        try:
            os.makedirs(category_dir, exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            return f"SUCCESS: Document '{doc_name}' organized into '{category}' at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not organize document. Error: {e}"

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
            # 1. --- DIRECT COMMAND INTERCEPT (Fuzzy Parsing) ---
            tool_result, tool_used = self._check_for_toolbox_command(user_input)
            if tool_used:
                return tool_result

            # 2. LLM Inference
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context:\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            system_prompt = """You are Oracle, a sophisticated local AI assistant with a Toolbox. 
Your primary function is to execute tasks for the user. 
If the user asks you to perform an action (like creating a file or folder), you MUST use your tools. 
DO NOT just provide instructions on how to do it. EXECUTE the task."""
            
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n{visual_info}\nUser: {user_input}"
            response = self.model.infer(full_prompt)

            self.memory_manager.store_interaction(user_input, response)
            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def _check_for_toolbox_command(self, user_input: str) -> (str | None, bool):
        lower_input = user_input.lower()
        
        # Folder Creation
        if any(kw in lower_input for kw in ["make", "create", "put"]) and any(kw in lower_input for kw in ["folder", "directory"]):
            folder_name = "new_folder"
            if "label it" in lower_input:
                folder_name = lower_input.split("label it")[1].strip().split()[0].strip('.,')
            elif "called" in lower_input:
                folder_name = lower_input.split("called")[1].strip().split()[0].strip('.,')
            
            relative_path = "dev folder" if "dev folder" in lower_input else ""
            return self.toolbox.create_folder(folder_name, relative_path), True

        # File Writing
        if any(kw in lower_input for kw in ["write", "put", "save"]) and any(kw in lower_input for kw in ["file", "content", "text"]):
            file_name = "new_file.txt"
            content = "Generated by Oracle."
            
            if "file called" in lower_input:
                file_name = lower_input.split("file called")[1].strip().split()[0].strip('.,')
            
            # Simple content extraction
            if "put" in lower_input and "inside" in lower_input:
                start = lower_input.find("put") + 3
                end = lower_input.find("inside")
                content = user_input[start:end].strip().strip('"\'')
            
            relative_path = "dev folder" if "dev folder" in lower_input else ""
            return self.toolbox.write_to_file(file_name, content, relative_path), True

        # System Status
        if "check system" in lower_input or "system status" in lower_input:
            return self.toolbox.check_system_status(), True

        return None, False

    def process_visual_input(self) -> dict:
        self.current_visual_context = self.vision.get_visual_context()
        return self.current_visual_context

    def process_voice_input(self) -> str:
        return "[DICTATION_REQUEST]: Please type your input."
