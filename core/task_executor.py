import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random
import shutil
import glob

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
        # Base paths for user's machine
        self.home = os.path.expanduser("~")
        self.desktop = os.path.join(self.home, "Desktop")
        self.documents = os.path.join(self.home, "Documents")
        self.dev_folder = "C:\\dev" if os.name == 'nt' else os.path.join(self.home, "oracle_dev")
        
        os.makedirs(self.dev_folder, exist_ok=True)

    def _resolve_path(self, path_str: str) -> str:
        """Resolves a path string to an absolute system path."""
        path_lower = path_str.lower()
        if "desktop" in path_lower:
            return self.desktop
        elif "documents" in path_lower:
            return self.documents
        elif "dev folder" in path_lower or "c:\\dev" in path_lower:
            return self.dev_folder
        elif os.path.isabs(path_str):
            return path_str
        else:
            # Default to home directory for general requests
            return self.home

    def list_files(self, directory: str = "dev folder") -> str:
        """Lists files in a directory so Oracle can 'see' what's there."""
        target = self._resolve_path(directory)
        try:
            files = os.listdir(target)
            return f"SUCCESS: Found {len(files)} items in {target}: {', '.join(files[:20])}"
        except Exception as e:
            return f"FAILURE: Could not list files in {target}. Error: {e}"

    def read_file(self, file_name: str, directory: str = "dev folder") -> str:
        """Reads the content of a file so Oracle can process the data."""
        target_dir = self._resolve_path(directory)
        final_path = os.path.join(target_dir, file_name)
        try:
            with open(final_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"SUCCESS: Read file {file_name}. Content: {content[:500]}..."
        except Exception as e:
            return f"FAILURE: Could not read file {final_path}. Error: {e}"

    def write_to_file(self, file_name: str, content: str, directory: str = "dev folder") -> str:
        """Writes content to a file."""
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
        """Creates a folder."""
        target_dir = self._resolve_path(directory)
        final_path = os.path.join(target_dir, folder_name)
        try:
            os.makedirs(final_path, exist_ok=True)
            return f"SUCCESS: Folder '{folder_name}' created at {final_path}."
        except Exception as e:
            return f"FAILURE: Could not create folder. Error: {e}"

    def search_files(self, pattern: str, directory: str = "dev folder") -> str:
        """Searches for files matching a pattern (e.g., *.txt)."""
        target = self._resolve_path(directory)
        try:
            matches = glob.glob(os.path.join(target, pattern))
            return f"SUCCESS: Found {len(matches)} matches for '{pattern}': {', '.join([os.path.basename(m) for m in matches[:10]])}"
        except Exception as e:
            return f"FAILURE: Search failed. Error: {e}"

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
        
        self.log_action("TaskExecutor initialized with Intelligence-Driven Agency.")
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
            # 1. --- INTELLIGENT TOOL INTERCEPT ---
            # We use a more advanced parser that allows for reading and processing
            tool_result, tool_used = self._intelligent_parser(user_input)
            if tool_used:
                # If the tool result is a 'READ' success, we feed it back to the LLM
                # so she can actually 'understand' the data she just retrieved.
                if "SUCCESS: Read file" in tool_result:
                    user_input = f"I have retrieved the data you asked for. Here is the content: {tool_result}\n\nNow, please complete the original request: {user_input}"
                else:
                    return tool_result

            # 2. --- LLM INFERENCE ---
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context:\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            system_prompt = """You are Oracle, a sophisticated local AI assistant with full agency over this device.
You are NOT a chatbot; you are an integrated agent. You can see files, read data, and manifest changes.
When the user asks you to process data from a file, use your 'read_file' tool first.
You have free reign to help the user across their Desktop, Documents, and Dev folders.
Always prioritize actual execution and data processing over just talking."""
            
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n{visual_info}\nUser: {user_input}"
            response = self.model.infer(full_prompt)

            self.memory_manager.store_interaction(user_input, response)
            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def _intelligent_parser(self, user_input: str) -> (str | None, bool):
        """Advanced parser for multi-step agency tasks."""
        lower_input = user_input.lower()
        
        # --- DATA RETRIEVAL (READING) ---
        if any(kw in lower_input for kw in ["read", "get data", "retrieve", "look at"]) and "file" in lower_input:
            file_name = ""
            for word in user_input.split():
                if "." in word: file_name = word.strip('.,')
            
            directory = "dev folder"
            if "desktop" in lower_input: directory = "desktop"
            elif "documents" in lower_input: directory = "documents"
            
            if file_name:
                return self.toolbox.read_file(file_name, directory), True

        # --- FILE LISTING ---
        if any(kw in lower_input for kw in ["list", "show", "what is in"]) and any(kw in lower_input for kw in ["folder", "directory", "desktop"]):
            directory = "dev folder"
            if "desktop" in lower_input: directory = "desktop"
            elif "documents" in lower_input: directory = "documents"
            return self.toolbox.list_files(directory), True

        # --- ORIGINAL WRITING/CREATION LOGIC ---
        if any(kw in lower_input for kw in ["write", "save", "create"]) and "file" in lower_input:
            file_name = "new_file.txt"
            if "called" in lower_input:
                file_name = lower_input.split("called")[1].strip().split()[0].strip('.,')
            
            content = "Generated by Oracle."
            if "content" in lower_input:
                content = user_input.split("content")[1].strip()
            
            directory = "dev folder"
            if "desktop" in lower_input: directory = "desktop"
            return self.toolbox.write_to_file(file_name, content, directory), True

        return None, False

    def process_visual_input(self) -> dict:
        self.current_visual_context = self.vision.get_visual_context()
        return self.current_visual_context

    def process_voice_input(self) -> str:
        return "[DICTATION_REQUEST]: Please type your input."
