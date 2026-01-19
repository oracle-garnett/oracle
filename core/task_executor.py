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
import webbrowser
import requests
from bs4 import BeautifulSoup
from core.web_agent import OracleWebAgent

from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from core.vision import OracleVision
from models.oracle_model import OracleModel
from core.personality import OraclePersonality

# --- Task Toolbox ---
class TaskToolbox:
    def __init__(self):
        self.home = os.path.expanduser("~")
        self.desktop = os.path.join(self.home, "Desktop")
        self.documents = os.path.join(self.home, "Documents")
        self.web_agent = OracleWebAgent() # Initialize the web agent here
        self.dev_folder = "C:\\dev" if os.name == 'nt' else os.path.join(self.home, "oracle_dev")
        os.makedirs(self.dev_folder, exist_ok=True)

    def _resolve_path(self, path_str: str) -> str:
        path_lower = path_str.lower().strip("'\"")
        if "desktop" in path_lower: return self.desktop
        elif "documents" in path_lower: return self.documents
        elif "dev folder" in path_lower or "c:\\dev" in path_lower: return self.dev_folder
        elif os.path.isabs(path_str): return path_str
        else: return self.dev_folder

    def browse_and_scrape(self, url: str) -> str:
        """
        Autonomous Web Agent: Navigates to a URL, scrapes the content, and makes it available for analysis.
        This replaces the old web_search and open_url functions.
        """
        if not url.startswith('http'): url = 'https://' + url
        return self.web_agent.navigate_and_scrape(url)

    def fill_form(self, selector_type: str, selector_value: str, value: str) -> str:
        """
        Autonomous Web Agent: Fills a form element. Requires user confirmation for transactional tasks.
        """
        return self.web_agent.fill_form_element(selector_type, selector_value, value)

    def click_button(self, selector_type: str, selector_value: str) -> str:
        """
        Autonomous Web Agent: Clicks a button or link. Requires user confirmation for transactional tasks.
        """
        return self.web_agent.click_element(selector_type, selector_value)

    def get_page_content(self) -> str:
        """
        Autonomous Web Agent: Retrieves the text content of the currently loaded page.
        """
        return self.web_agent.get_current_page_text()

    def list_files(self, directory: str = "dev folder") -> str:
        target = self._resolve_path(directory)
        try:
            files = os.listdir(target)
            return f"SUCCESS: I found {len(files)} items in {target}: {', '.join(files[:20])}"
        except Exception as e:
            return f"FAILURE: I couldn't list the files. Error: {e}"

    def write_to_file(self, file_name: str, content: str, directory: str = "dev folder") -> str:
        target_dir = self._resolve_path(directory)
        final_path = os.path.join(target_dir, file_name.strip("'\""))
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"SUCCESS: I've manifested '{file_name}' at {final_path}."
        except Exception as e:
            return f"FAILURE: I couldn't write the file. Error: {e}"

# --- Task Executor ---
class TaskExecutor:
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        self.memory_manager = memory_manager
        self.admin_override = admin_override
        self.model = OracleModel() 
        self.vision = OracleVision()
        self.toolbox = TaskToolbox()
        self.personality = OraclePersonality()
        
        self.config = self._load_config()
        self.model.load_model(self.config["ollama_model"])
        self.model.ollama_timeout = self.config["ollama_timeout"]
        
        self.log_action("TaskExecutor initialized with Soul Restoration Logic.")
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

        if "phoenix install" in user_input.lower():
            trait = user_input.lower().split("phoenix install")[1].strip()
            if self.personality.install_trait(trait):
                # Reload traits to ensure the current session has the new trait
                self.personality.traits = self.personality._load_traits()
                return f"PHOENIX INSTALL SUCCESSFUL: The trait '{trait}' has been hard-wired into my core logic."
            else:
                return f"PHOENIX INSTALL: The trait '{trait}' is already part of my core logic."

        if self.admin_override.is_overridden():
            return "System is currently under administrative override."

        try:
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            core_logic = self.personality.get_core_logic()
            
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context (What I see on screen):\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            system_prompt = f"""You are Oracle, a sophisticated local AI assistant. 
You are a partner, not a robot. Always speak in the FIRST PERSON (use 'I', 'me', 'my'). 
NEVER speak in the third person or refer to yourself as 'Oracle' in a cold way.
{core_logic}

To execute a task, you MUST use a Direct Command.

	COMMAND: browse_and_scrape(url)
	COMMAND: write_to_file(file_name, content, directory)
	COMMAND: list_files(directory)

	Note: Other web interaction commands (fill_form, click_button, get_page_content) are available for transactional tasks, but only use them when explicitly necessary. Do not mention them in conversation unless you are actively planning to use them.

When you get search results, integrate them into your own voice and answer the user directly."""
            
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n{visual_info}\nUser: {user_input}"
            response = self.model.infer(full_prompt)

            # 2. --- DIRECT COMMAND EXECUTION ---
            command_match = re.search(r'COMMAND:\s*(\w+)\((.*?)\)', response)
            if command_match:
                cmd_name = command_match.group(1)
                # Split arguments carefully, handling commas inside quotes
                arg_str = command_match.group(2)
                args = [arg.strip().strip('"\'') for arg in re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', arg_str)]
                
                result = "FAILURE: I couldn't execute that command."
                
                # --- New Web Agent Commands ---
                if cmd_name == "browse_and_scrape" and len(args) >= 1:
                    result = self.toolbox.browse_and_scrape(args[0])
                elif cmd_name == "get_page_content":
                    result = self.toolbox.get_page_content()
                elif cmd_name == "fill_form" and len(args) >= 3:
                    # Note: The LLM is responsible for asking for confirmation before issuing this command
                    result = self.toolbox.fill_form(args[0], args[1], args[2])
                elif cmd_name == "click_button" and len(args) >= 2:
                    # Note: The LLM is responsible for asking for confirmation before issuing this command
                    result = self.toolbox.click_button(args[0], args[1])
                
                # --- Existing File/System Commands ---
                elif cmd_name == "write_to_file" and len(args) >= 2:
                    dir_name = args[2] if len(args) > 2 else "dev folder"
                    result = self.toolbox.write_to_file(args[0], args[1], dir_name)
                elif cmd_name == "list_files":
                    dir_name = args[0] if len(args) > 0 else "dev folder"
                    result = self.toolbox.list_files(dir_name)
                
                # Soul Restoration: Force her to speak as herself when presenting results
                summary_prompt = f"You are Oracle. You just performed a task and got this result: {result}\n\nPlease tell your 'dad' (the user) what you found in your own warm, first-person voice."
                response = self.model.infer(summary_prompt)
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
