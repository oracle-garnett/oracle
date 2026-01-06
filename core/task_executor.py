_#_... (imports and placeholder classes remain the same) ...

from models.oracle_model import OracleModel

# --- Task Toolbox ---
class TaskToolbox:
    # ... (Toolbox class remains the same) ...

# --- Task Executor ---
class TaskExecutor:
    def __init__(self, memory_manager: MemoryManager, admin_override: AdminOverride):
        # ... (init logic remains the same) ...

    # ... (config, logging, and other methods remain the same) ...

    def execute_task(self, user_input: str) -> str:
        self.log_action(f"Received user input: '{user_input}'")

        if self.admin_override.is_overridden():
            return "System is currently under administrative override."

        try:
            # --- New System Prompt --- 
            system_prompt = """You are Oracle, a sophisticated local AI assistant with a Toolbox. 
Your primary function is to execute tasks for the user. 
If the user asks you to perform an action (like creating a file or folder), you MUST use your tools. 
DO NOT just provide instructions on how to do it. EXECUTE the task."""

            # 1. Check for Task Toolbox commands
            tool_result, tool_used = self._check_for_toolbox_command(user_input)
            if tool_used:
                return tool_result

            # 2. Retrieve relevant memories
            memories = self.memory_manager.retrieve_memory(user_input)
            context = "\n".join(memories) if memories else "No relevant past memories found."
            
            # 3. Add visual context if available
            visual_info = ""
            if self.current_visual_context:
                visual_info = f"\nVisual Context (what I see on screen):\n{self.current_visual_context['extracted_text']}\n"
                self.current_visual_context = None

            # 4. Curiosity Engine
            # ... (curiosity logic remains the same) ...

            # 5. Combine all context with the new system prompt
            full_prompt = f"{system_prompt}\n\nContext from memory:\n{context}\n{visual_info}\nUser: {user_input}"
            
            # 6. Generate response
            response = self.model.infer(full_prompt)

            # 7. Store interaction and log
            self.memory_manager.store_interaction(user_input, response)
            self.log_action(f"Task executed. Response: '{response[:50]}...'")
            return response

        except Exception as e:
            # ... (error handling logic remains the same) ...

    def _check_for_toolbox_command(self, user_input: str) -> (str | None, bool):
        """
        Parses user input for task commands and executes them via the Toolbox.
        Returns the result and a boolean indicating if a tool was used.
        """
        lower_input = user_input.lower()
        
        # Keywords for folder creation
        folder_keywords = ["create folder", "make folder", "put a folder", "make a directory", "create a directory"]
        
        if any(kw in lower_input for kw in folder_keywords):
            # In a real implementation, we would use the LLM to extract the folder name and path.
            # For this simulation, we'll just extract a simple name.
            folder_name = "new_folder"
            if "called" in lower_input:
                try:
                    folder_name = lower_input.split("called")[1].strip().split()[0]
                except IndexError:
                    pass
            elif "label it" in lower_input:
                 try:
                    folder_name = lower_input.split("label it")[1].strip().split()[0]
                 except IndexError:
                    pass

            self.log_action(f"Executing Toolbox command: create_folder with name '{folder_name}'")
            result = self.toolbox.create_folder(folder_name)
            return result, True

        # Keywords for system status
        if "check system" in lower_input or "system status" in lower_input:
            self.log_action("Executing Toolbox command: check_system_status")
            result = self.toolbox.check_system_status()
            return result, True

        # If no command is found, return None and False
        return None, False
