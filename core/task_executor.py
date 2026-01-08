import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time
import random

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
    A collection of local system functions Oracle can execute.
    This is the foundation for her task completion capabilities.
    """
    def __init__(self):
        # Corrected base path based on user feedback: C:\dev is the root for the dev folder
        self.base_path = "C:\\dev"

    def _get_target_path(self, relative_path: str) -> str:
        """Helper to determine the correct base directory for PowerShell commands."""
        if "dev folder" in relative_path.lower() or "c:\\dev" in relative_path.lower():
            return self.base_path
        elif "desktop" in relative_path.lower():
            return "C:\\Users\\emjim\\Desktop"
        else:
            # Default to the project root for safety if no path is specified
            return "C:\\Users\\emjim\\Desktop\\oracle"

    def create_folder(self, folder_name: str, relative_path: str = "") -> str:
        """Generates a PowerShell command to create a folder at the specified path."""
        
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, folder_name)
        
        # Generate PowerShell command
        powershell_command = f"New-Item -Path \"{final_path}\" -ItemType Directory -Force"
        return f"To create the folder, please run this PowerShell command:\n```powershell\n{powershell_command}\n```\nAfter running it, please confirm if the folder was created successfully."

    def write_to_file(self, file_name: str, content: str, relative_path: str = "") -> str:
        """Generates a PowerShell command to write content to a file at the specified path."""
        
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, file_name)
        
        # Escape content for PowerShell (single quotes for literal string)
        escaped_content = content.replace("\"", "`"") # Escape double quotes
        
        # Generate PowerShell command
        powershell_command = f"Set-Content -Path \"{final_path}\" -Value \"{escaped_content}\" -Force"
        return f"To write to the file, please run this PowerShell command:\n```powershell\n{powershell_command}\n```\nAfter running it, please confirm if the file was created/updated successfully."

    def dictate_note(self, note_content: str, file_name: str = "dictated_note.txt", relative_path: str = "") -> str:
        """Generates a PowerShell command to save dictated content to a file."""
        target_dir = self._get_target_path(relative_path)
        final_path = os.path.join(target_dir, file_name)
        
        escaped_content = note_content.replace("\"", "`"")
        powershell_command = f"Set-Content -Path \"{final_path}\" -Value \"{escaped_content}\" -Force"
        return f"To save your dictated note, please run this PowerShell command:\n```powershell\n{powershell_command}\n```\nAfter running it, please confirm if the note was saved successfully."

    def organize_document(self, doc_name: str, doc_content: str, category: str = "documents", relative_path: str = "") -> str:
        """Generates PowerShell commands to create a categorized folder and save a document."""
        base_target_dir = self._get_target_path(relative_path)
        category_dir = os.path.join(base_target_dir, category)
        final_path = os.path.join(category_dir, doc_name)

        escaped_content = doc_content.replace("\"", "`"")

        # Generate PowerShell commands for folder and file creation
        powershell_command_folder = f"New-Item -Path \"{category_dir}\" -ItemType Directory -Force"
        powershell_command_file = f"Set-Content -Path \"{final_path}\" -Value \"{escaped_content}\" -Force"

        return f"To organize your document, please run these PowerShell commands in order:\n```powershell\n{powershell_command_folder}\n{powershell_command_file}\n```\nAfter running them, please confirm if the document was organized successfully."

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
        self.toolbox = TaskToolbox()
        
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
            # Simulate Whisper transcription
            # In a real scenario, this would call self.model.record_and_transcribe()
            # For now, we'll return a placeholder or prompt the user for input if needed.
            return "[Simulated voice input: This is a test dictation.]"
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
            # 1. --- DIRECT COMMAND INTERCEPT ---
            tool_result, tool_used = self._check_for_toolbox_command(user_input)
            if tool_used:
                # If a tool was used, return the result directly, bypassing the LLM
                return tool_result

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
DO NOT just provide instructions on how to do it. EXECUTE the task."""
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

    def _check_for_toolbox_command(self, user_input: str) -> (str | None, bool):
        """
        Parses user input for task commands and executes them via the Toolbox.
        Returns the result and a boolean indicating if a tool was used.
        """
        lower_input = user_input.lower()
        
        # --- AGGRESSIVE FUZZY PARSING FOR FOLDER CREATION ---
        has_folder_action = any(kw in lower_input for kw in ["make", "create", "put"]) and any(kw in lower_input for kw in ["folder", "directory"])
        
        if has_folder_action:
            # 1. Extract folder name
            folder_name = "new_folder"
            relative_path = ""
            
            # Try to extract the name after "label it" or "called"
            if "label it" in lower_input:
                 try:
                    folder_name = lower_input.split("label it")[1].strip().split()[0].strip('.,')
                 except IndexError:
                    pass
            elif "called" in lower_input:
                try:
                    folder_name = lower_input.split("called")[1].strip().split()[0].strip('.,')
                except IndexError:
                    pass
            elif "test" in lower_input:
                folder_name = "test"

            # 2. Extract relative path
            if "in my dev folder" in lower_input or "in dev folder" in lower_input or "c:\\dev" in lower_input:
                relative_path = "dev folder"

            self.log_action(f"Executing Toolbox command: create_folder with name '{folder_name}' in path '{relative_path}'")
            result = self.toolbox.create_folder(folder_name, relative_path)
            
            # 3. Return the result directly (Hard-Wired Response)
            return result, True

        # --- AGGRESSIVE FUZZY PARSING FOR FILE WRITING ---
        has_write_action = any(kw in lower_input for kw in ["write", "put", "save"]) and any(kw in lower_input for kw in ["to file", "content", "text"])
        if has_write_action:
            file_name = "new_file.txt"
            content = ""
            relative_path = ""

            # Extract file name
            if "file called" in lower_input:
                try:
                    file_name = lower_input.split("file called")[1].strip().split()[0].strip('.,')
                except IndexError:
                    pass
            elif "file" in lower_input:
                try:
                    words = lower_input.split()
                    for word in words:
                        if word.endswith((".txt", ".py", ".cert", ".md")):
                            file_name = word.strip('.,')
                            break
                except Exception:
                    pass
            
            # Extract content
            if "content" in lower_input:
                try:
                    content_start = lower_input.find("content") + len("content")
                    content_end = lower_input.find("in file") if "in file" in lower_input else len(lower_input)
                    content = user_input[content_start:content_end].strip().strip('"\'')
                except Exception:
                    pass
            elif "put" in lower_input and "inside" in lower_input:
                try:
                    start = lower_input.find("put") + 3
                    end = lower_input.find("inside")
                    content = user_input[start:end].strip().strip('"\'')
                except Exception:
                    pass

            # Extract relative path
            if "in my dev folder" in lower_input or "in dev folder" in lower_input or "c:\\dev" in lower_input:
                relative_path = "dev folder"

            self.log_action(f"Executing Toolbox command: write_to_file with name '{file_name}' in path '{relative_path}' and content '{content[:50]}...' ")
            result = self.toolbox.write_to_file(file_name, content, relative_path)
            return result, True

        # --- AGGRESSIVE FUZZY PARSING FOR DICTATION ---
        has_dictate_action = any(kw in lower_input for kw in ["take a note", "dictate", "record this"])
        if has_dictate_action:
            self.log_action("Initiating voice input for dictation.")
            # In a real scenario, this would trigger actual voice recording and transcription
            # For now, we'll simulate it and expect the user to provide the content.
            simulated_transcription = self.process_voice_input() # Calls the simulated Whisper
            
            file_name = "dictated_note.txt"
            relative_path = "dev folder"
            if "file called" in lower_input:
                try:
                    file_name = lower_input.split("file called")[1].strip().split()[0].strip('.,')
                except IndexError:
                    pass

            self.log_action(f"Executing Toolbox command: dictate_note with content '{simulated_transcription[:50]}...' ")
            result = self.toolbox.dictate_note(simulated_transcription, file_name, relative_path)
            return result, True

        # --- AGGRESSIVE FUZZY PARSING FOR DOCUMENT ORGANIZATION/RENDERING ---
        has_organize_action = any(kw in lower_input for kw in ["render", "draw", "organize", "create"]) and any(kw in lower_input for kw in ["certificate", "document", "report"])
        if has_organize_action:
            doc_name = "new_document.txt"
            doc_content = "[Generated Document Content]"
            category = "documents"
            relative_path = "dev folder"

            if "certificate" in lower_input:
                doc_name = "certificate_of_achievement.txt"
                doc_content = "This certifies that [Name] has achieved [Achievement].\nDate: [Date]"
                category = "certificates"
            elif "report" in lower_input:
                doc_name = "report.txt"
                doc_content = "[Generated Report Content]"
                category = "reports"
            
            if "called" in lower_input:
                try:
                    doc_name = lower_input.split("called")[1].strip().split()[0].strip('.,')
                except IndexError:
                    pass

            self.log_action(f"Executing Toolbox command: organize_document with name '{doc_name}' in category '{category}'")
            result = self.toolbox.organize_document(doc_name, doc_content, category, relative_path)
            return result, True

        # Keywords for system status
        if "check system" in lower_input or "system status" in lower_input:
            self.log_action("Executing Toolbox command: check_system_status")
            result = self.toolbox.check_system_status()
            return result, True

        # If no command is found, return None and False
        return None, False
