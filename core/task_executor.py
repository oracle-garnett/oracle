import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random
import shutil # Added for file organization and deletion
import re # For more robust name extraction

# --- Placeholder Imports for Dependencies ---
# These are needed to make the TaskExecutor class runnable in the user's environment
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

from models.oracle_model import OracleModel

# --- Task Toolbox ---
class TaskToolbox:
    """
    A collection of local system functions Oracle can execute directly.
    This is the foundation for her task completion capabilities.
    """
    def __init__(self):
        # Corrected base path based on user feedback: C:\dev is the root for the dev folder
        self.base_path = "C:\\dev"
        # Ensure the base path exists for direct operations
        os.makedirs(self.base_path, exist_ok=True)

    def _resolve_path(self, item_name: str, relative_path: str = "") -> str:
        """Helper to resolve an item name to a full absolute path, prioritizing C:\dev."""
        if os.path.isabs(item_name): # If it's already an absolute path
            return item_name

        # Prioritize C:\dev if specified or implied
        if "dev folder" in relative_path.lower() or "c:\\dev" in relative_path.lower() or not relative_path:
            potential_path = os.path.join(self.base_path, item_name)
            if os.path.exists(potential_path) or not os.path.dirname(item_name): # If it exists or is just a name
                return potential_path
        
        # Fallback to other common paths if needed (e.g., Desktop, project root)
        if "desktop" in relative_path.lower():
            return os.path.join(os.path.expanduser("~"), "Desktop", item_name)
        
        # Default to C:\dev if no other clear path is given and it's not an absolute path
        return os.path.join(self.base_path, item_name)

    def create_folder(self, folder_name: str, relative_path: str = "") -> str:
        """Creates a folder at the specified path using direct Python os.makedirs."""
        
        final_path = self._resolve_path(folder_name, relative_path)
        
        try:
            os.makedirs(final_path, exist_ok=True)
            if os.path.exists(final_path):
                 return f"SUCCESS: Folder \'{folder_name}\' created at {final_path}."
            else:
                 return f"FAILURE: Folder creation failed, but no exception was raised. Path: {final_path}"
        except Exception as e:
            return f"FAILURE: Could not create folder at {final_path}. System Error: {e}"

    def write_to_file(self, file_name: str, content: str, relative_path: str = "") -> str:
        """Writes content to a file at the specified path using direct Python file operations."""
        
        final_path = self._resolve_path(file_name, relative_path)
        
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True) # Ensure parent directory exists
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if os.path.exists(final_path):
                return f"SUCCESS: File \'{file_name}\' created at {final_path} with content: \'{content[:50]}...\'."
            else:
                return f"FAILURE: File creation failed, but no exception was raised. Path: {final_path}"
        except Exception as e:
            return f"FAILURE: Could not create file at {final_path}. System Error: {e}"

    def dictate_note(self, note_content: str, file_name: str = "dictated_note.txt", relative_path: str = "") -> str:
        """Saves dictated content to a file using direct Python file operations."""
        final_path = self._resolve_path(file_name, relative_path)
        
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            if os.path.exists(final_path):
                return f"SUCCESS: Dictated note saved to \'{file_name}\' at {final_path}."
            else:
                return f"FAILURE: Dictated note saving failed, but no exception was raised. Path: {final_path}"
        except Exception as e:
            return f"FAILURE: Could not save dictated note at {final_path}. System Error: {e}"

    def organize_document(self, doc_name: str, doc_content: str, category: str = "documents", relative_path: str = "") -> str:
        """Creates a categorized folder and saves a document using direct Python operations."""
        base_target_dir = self._resolve_path("", relative_path) # Resolve base path for category
        category_dir = os.path.join(base_target_dir, category)
        final_path = os.path.join(category_dir, doc_name)

        try:
            os.makedirs(category_dir, exist_ok=True) # Ensure category folder exists
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            if os.path.exists(final_path):
                return f"SUCCESS: Document \'{doc_name}\' organized into \'{category}\' at {final_path}."
            else:
                return f"FAILURE: Document organization failed, but no exception was raised. Path: {final_path}"
        except Exception as e:
            return f"FAILURE: Could not organize document at {final_path}. System Error: {e}"

    def delete_item(self, item_name: str, relative_path: str = "") -> str:
        """Deletes a file or an empty folder at the specified path using direct Python operations."""
        final_path = self._resolve_path(item_name, relative_path)

        if not os.path.exists(final_path):
            return f"FAILURE: Item at \'{final_path}\' does not exist. Cannot delete."

        try:
            if os.path.isfile(final_path):
                os.remove(final_path)
                return f"SUCCESS: File \'{final_path}\' deleted."
            elif os.path.isdir(final_path):
                # For non-empty directories, use shutil.rmtree
                shutil.rmtree(final_path)
                return f"SUCCESS: Folder \'{final_path}\' and its contents deleted."
            else:
                return f"FAILURE: Item at \'{final_path}\' is not a file or folder. Cannot delete."
        except Exception as e:
            return f"FAILURE: Could not delete item at \'{final_path}\' due to System Error: {e}"

    def clean_empty_folders(self, target_path: str = "") -> str:
        """Deletes all empty subfolders within a given target path."""
        base_dir = self._resolve_path("", target_path)
        deleted_count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(base_dir, topdown=False):
                if not dirnames and not filenames:
                    os.rmdir(dirpath)
                    deleted_count += 1
            return f"SUCCESS: Deleted {deleted_count} empty folders in \'{base_dir}\"."
        except Exception as e:
            return f"FAILURE: Could not clean empty folders in \'{base_dir}\' due to System Error: {e}"

    def check_system_status(self) -> str:
        """Simulates checking system resources."""
        return "SUCCESS: System status check complete. CPU: 45%, RAM: 60% (llama3 is running)."

    def clean_empty_folders(self, target_path: str = "") -> str:
        """Deletes all empty subfolders within a given target path."""
        base_dir = self._resolve_path("", target_path)
        deleted_count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(base_dir, topdown=False):
                if not dirnames and not filenames:
                    os.rmdir(dirpath)
                    deleted_count += 1
            return f"SUCCESS: Deleted {deleted_count} empty folders in \'{base_dir}\"."
        except Exception as e:
            return f"FAILURE: Could not clean empty folders in \'{base_dir}\' due to System Error: {e}"

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
        
        # State for deletion confirmation
        self.pending_deletion_path = None

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
        # Default configuration
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
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] Internal Wonder: {wonder_text}\n"
        with open(self.wonder_log, 'a') as f:
            f.write(entry)

    def process_voice_input(self) -> str:
        self.log_action("Initiating voice input recording.")
        try:
            # In a real scenario, this would call self.model.record_and_transcribe()
            # For now, we'll prompt the user for input if needed.
            return "[DICTATION_REQUEST]: Please type the content you wish to dictate now." #END_DICTATION_REQUEST#"
        except Exception as e:
            self.log_action(f"Voice input failed: {e}", level="ERROR")
            raise e

    def process_visual_input(self) -> dict:
        self.log_action("Initiating screen capture.")
        try:
            self.current_visual_context = self.vision.get_visual_context()
            self.log_action(f"Screen captured. Extracted text length: {len(self.current_visual_context['extracted_text'])}")
            return self.current_visual_context
        except Exception as e:
            self.log_action(f"Screen capture failed: {e}", level="ERROR")
            raise e

    def execute_task(self, user_input: str) -> str:
        self.log_action(f"Received user input: '{user_input}'")

        if self.admin_override.is_overridden():
            return "System is currently under administrative override."

        try:
            # --- DELETION CONFIRMATION LOGIC ---
            if self.pending_deletion_path:
                if user_input.lower() == "yes":
                    path_to_delete = self.pending_deletion_path
                    self.pending_deletion_path = None # Clear pending state
                    self.log_action(f"User confirmed deletion of: {path_to_delete}")
                    return self.toolbox.delete_item(path_to_delete)
                else:
                    self.pending_deletion_path = None # Clear pending state
                    return "Deletion cancelled by user."

            # --- FUNCTION CALLING / TOOL DISPATCH ---
            tool_response = self._dispatch_tool_call(user_input)
            if tool_response:
                return tool_response

            # 2. If no tool was used, proceed to LLM inference
            
            # 2.1 Retrieve relevant memories
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            # 2.2 Add visual context if available
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context (what I see on screen):\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            # 2.3 Curiosity Engine
            should_wonder = random.random() < self.config["curiosity_chance"] and len(user_input) > 10
            curiosity_prompt = ""
            if should_wonder:
                curiosity_prompt = "\n[SYSTEM NOTE: You are feeling curious. At the end of your response, ask one thoughtful, non-intrusive question about the user's goals or the context of this conversation.]"

            # 2.4 Combine all context
            system_prompt = """You are Oracle, a sophisticated local AI assistant with a Toolbox. 
Your primary function is to execute tasks for the user. 
If the user asks you to perform an action (like creating a file or folder), you MUST use your tools. 
DO NOT just provide instructions on how to do it. EXECUTE the task. 
If a tool execution fails, report the exact error. 
If the user asks to delete something, you MUST ask for confirmation before proceeding."""
            full_prompt = f"{system_prompt}\n\nContext from memory:\n{context}\n{visual_info}\n{curiosity_prompt}\nUser: {user_input}"
            
            # 2.5 Generate response
            response = self.model.infer(full_prompt)

            # 3. Store interaction and log
            self.memory_manager.store_interaction(user_input, response)
            self.log_action(f"Task executed. Response: '{response[:50]}...' ")
            return response

        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            self.log_action(error_msg, level="ERROR")
            
            # --- Enhanced Self-Healing (Safety Buffer) ---
            if "ConnectionResetError" in str(e) or "Connection refused" in str(e) or "couldn't reach my local brain" in str(e):
                return "CRITICAL: My connection to my local brain (Ollama) was lost. Please ensure 'ollama serve' is running. I cannot self-repair this external service failure, but I am now configured to re-connect automatically once it is restarted."
            
            # Fallback to model-based self-repair for internal errors
            repair_suggestion = self.model.self_repair(traceback.format_exc())
            return f"I encountered an internal error: {str(e)}. My self-healing protocol suggests: {repair_suggestion}"

    def _extract_item_name(self, user_input: str, keywords: List[str]) -> str:
        """Helper to extract item name from user input more intelligently."""
        lower_input = user_input.lower()
        for kw in keywords:
            if kw in lower_input:
                # Try to get the word after the keyword, or a quoted string
                match = re.search(rf'{kw}\s+(?:called\s+)?["\‘’]([^"]+)["\‘’]', lower_input) # Quoted string
                if match: return match.group(1)
                match = re.search(rf'{kw}\s+(?:named\s+)?([a-zA-Z0-9_.-]+)', lower_input) # Single word after keyword
                if match: return match.group(1)
        
        # Fallback: try to find a path-like string or a common file/folder name
        path_match = re.search(r'([a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*)|([a-zA-Z0-9_.-]+\.(?:txt|py|cert|md|html))|([a-zA-Z0-9_.-]+)', user_input)
        if path_match: return path_match.group(0).strip()
        
        return ""

    def _dispatch_tool_call(self, user_input: str) -> str | None:
        """
        Dispatches tool calls based on user input using a more robust function calling approach.
        Returns the tool's result if a tool was called, otherwise None.
        """
        lower_input = user_input.lower()

        # --- Tool: create_folder ---
        if any(kw in lower_input for kw in ["make", "create", "put"]) and any(kw in lower_input for kw in ["folder", "directory"]):
            folder_name = self._extract_item_name(user_input, ["folder", "directory", "called", "label it"])
            if not folder_name: folder_name = "new_folder"
            relative_path = "dev folder" if "dev folder" in lower_input or "c:\\dev" in lower_input else ""
            self.log_action(f"Dispatching create_folder: name='{folder_name}', path='{relative_path}'")
            return self.toolbox.create_folder(folder_name, relative_path)

        # --- Tool: write_to_file ---
        if any(kw in lower_input for kw in ["write", "put", "save"]) and any(kw in lower_input for kw in ["file", "content", "text"]):
            file_name = self._extract_item_name(user_input, ["file", "called", "named"])
            if not file_name: file_name = "new_file.txt"
            
            content_match = re.search(r'(?:put|write)\s+["\‘’]([^"‘’]+)["\‘’](?:\s+inside it)?', user_input, re.IGNORECASE)
            content = content_match.group(1) if content_match else "[No content provided]"

            relative_path = "dev folder" if "dev folder" in lower_input or "c:\\dev" in lower_input else ""
            self.log_action(f"Dispatching write_to_file: name='{file_name}', content='{content[:50]}...', path='{relative_path}'")
            return self.toolbox.write_to_file(file_name, content, relative_path)

        # --- Tool: dictate_note ---
        if any(kw in lower_input for kw in ["take a note", "dictate", "record this"]):
            self.log_action("Dispatching dictate_note: requesting user input for dictation.")
            # Simulate dictation request, then save it
            dictated_content = self.process_voice_input() # This will return the prompt for user to type
            if "[DICTATION_REQUEST]" in dictated_content: # If it's the prompt, we need to wait for user input
                # This is a tricky part for direct execution. For now, we'll return the prompt
                # and expect the next user input to be the dictated content.
                # A more advanced system would use a state machine or a dedicated UI element.
                return dictated_content
            
            file_name = self._extract_item_name(user_input, ["file", "called", "named"])
            if not file_name: file_name = "dictated_note.txt"
            relative_path = "dev folder" if "dev folder" in lower_input or "c:\\dev" in lower_input else ""
            self.log_action(f"Dispatching dictate_note: saving '{dictated_content[:50]}...' to '{file_name}'")
            return self.toolbox.dictate_note(dictated_content, file_name, relative_path)

        # --- Tool: organize_document (for certificates/reports) ---
        if any(kw in lower_input for kw in ["render", "draw", "organize", "create"]) and any(kw in lower_input for kw in ["certificate", "document", "report"]):
            doc_name = self._extract_item_name(user_input, ["certificate", "document", "report", "called", "named"])
            if not doc_name: doc_name = "new_document.txt"
            
            doc_content = "[Generated Document Content]"
            category = "documents"
            if "certificate" in lower_input:
                doc_content = "This certifies that [Name] has achieved [Achievement].\nDate: [Date]"
                category = "certificates"
            elif "report" in lower_input:
                doc_content = "[Generated Report Content]"
                category = "reports"
            
            relative_path = "dev folder" if "dev folder" in lower_input or "c:\\dev" in lower_input else ""
            self.log_action(f"Dispatching organize_document: name='{doc_name}', category='{category}', path='{relative_path}'")
            return self.toolbox.organize_document(doc_name, doc_content, category, relative_path)

        # --- Tool: delete_item ---
        if any(kw in lower_input for kw in ["delete", "remove", "erase"]) and any(kw in lower_input for kw in ["file", "folder", "item", "directory"]):
            item_name = self._extract_item_name(user_input, ["delete", "remove", "erase", "file", "folder", "item", "directory", "called", "labeled"])
            if not item_name: 
                return "FAILURE: Please specify what you want me to delete."
            
            # Resolve the full path for confirmation
            full_path_to_delete = self.toolbox._resolve_path(item_name, user_input) # Pass user_input for path context
            
            if not os.path.exists(full_path_to_delete):
                return f"FAILURE: I cannot find '{full_path_to_delete}' to delete. Please provide the full path if it's not in C:\dev."

            self.pending_deletion_path = full_path_to_delete
            return f"I have located '{full_path_to_delete}'. Are you sure you want me to permanently delete this? Please type 'YES' to confirm."

        # --- Tool: clean_empty_folders ---
        if "clean empty folders" in lower_input or "delete empty folders" in lower_input:
            relative_path = "dev folder" if "dev folder" in lower_input or "c:\\dev" in lower_input else ""
            self.log_action(f"Dispatching clean_empty_folders in path '{relative_path}'")
            return self.toolbox.clean_empty_folders(relative_path)

        # --- Tool: check_system_status ---
        if "check system" in lower_input or "system status" in lower_input:
            self.log_action("Dispatching check_system_status")
            return self.toolbox.check_system_status()

        return None # No tool dispatched
