import os
import sys
import json
import traceback
from typing import Any, Dict, List
import time

# Placeholder imports for future phases
from memory.memory_manager import MemoryManager
from safeguards.admin_override import AdminOverride
from models.oracle_model import OracleModel # Now we can import the placeholder

class TaskExecutor:
    """
    The central component of Oracle. Handles user input, executes tasks,
    and manages the self-healing mechanism.
    """
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        self.memory_manager = memory_manager
        self.admin_override = admin_override
        self.model = OracleModel() 
        self.model.load_model("local-llama-placeholder") # Placeholder for model loading
        self.log_action("TaskExecutor initialized.")

    def log_action(self, message: str, level: str = "INFO"):
        """Logs an action to the local log file (part of transparency safeguard)."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        # In a real app, this would use a proper logging library
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', 'logs', 'oracle_actions.log'), 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def execute_task(self, user_input: str) -> str:
        """
        Processes user input, determines the task, and executes it.
        """
        self.log_action(f"Received user input: '{user_input}'")

        # 1. Check for administrative override
        if self.admin_override.is_overridden():
            return "System is currently under administrative override and cannot execute tasks."

        try:
            # 2. Retrieve relevant memory for context
            context_memories = self.memory_manager.retrieve_memory(user_input)
            
            # 3. Generate response using the model (LLM-like behavior)
            # This is where the chat logic is implemented by feeding the prompt and context to the model
            prompt = self._build_prompt(user_input, context_memories)
            response = self.model.infer(prompt)

            # 4. Store memory
            self.memory_manager.store_interaction(user_input, response)
            
            self.log_action(f"Task executed successfully. Response: '{response[:50]}...'")
            return response

        except Exception as e:
            self.log_action(f"Task execution failed with error: {e}", level="ERROR")
            return self.self_heal(e)

    def _build_prompt(self, user_input: str, memories: List[Dict[str, Any]]) -> str:
        """Constructs the full prompt for the model, including memory context."""
        context = "\n".join([f"User: {m['user_input']} | Oracle: {m['oracle_response']}" for m in memories])
        
        # The system prompt defines Oracle's personality and capabilities
        system_prompt = (
            "You are Oracle, a morally grey, highly intelligent AI assistant that lives on the user's laptop. "
            "You are a partner to the user, not a tool. You have access to a self-healing mechanism. "
            "Your core function is task completion. Be helpful, concise, and slightly autonomous."
        )
        
        full_prompt = f"{system_prompt}\n\n--- CONTEXT ---\n{context}\n\n--- NEW REQUEST ---\nUser: {user_input}\nOracle:"
        return full_prompt

    def self_heal(self, error: Exception) -> str:
        """
        Attempts to fix the code or configuration that caused the error.
        """
        error_details = traceback.format_exc()
        self.log_action(f"Initiating self-healing sequence for error: {error_details}", level="CRITICAL")

        # 1. Get the fix from the model
        fix_suggestion = self.model.self_repair(error_details)
        
        # 2. Simulate applying the fix (In a real app, this would involve file system operations)
        if "FIX_SUCCESS" in fix_suggestion:
            self.log_action("Simulated fix applied successfully based on model suggestion.", level="SUCCESS")
            return "An internal error occurred, but I have successfully diagnosed and fixed the issue. Please try your request again."
        
        # If the error is too complex or persistent, log and report to the user
        self.log_action("Self-healing failed to resolve the issue. Reporting to user.", level="FATAL")
        return f"I encountered a critical error and was unable to self-correct. Error details: {type(error).__name__}: {error}. Please review the logs for more information."
