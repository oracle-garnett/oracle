import time
import sys
import os
import subprocess
from core.task_executor import TaskExecutor
from safeguards.admin_override import AdminOverride
from safeguards.resource_monitor import ResourceMonitor
from memory.memory_manager import MemoryManager
from ui.floating_panel import OracleUI

def initialize_oracle():
    """Initializes all core components of the Oracle AI assistant."""
    print("Initializing Oracle AI Assistant...")

    # 1. Initialize Safeguards
    admin_override = AdminOverride()
    resource_monitor = ResourceMonitor()
    
    # 2. Initialize Memory Manager
    memory_manager = MemoryManager(secret_key="oracle-default-secret-key")

    # 3. Initialize Core Executor
    task_executor = TaskExecutor(memory_manager, admin_override)

    print("Oracle initialization complete.")
    return task_executor, admin_override, resource_monitor

def trigger_auto_save():
    """Triggers the savepoint script to ensure memory persistence on shutdown."""
    print("\n--- Oracle Shutdown Protocol: Initiating Auto-Save ---")
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'create_savepoint.py')
        # Run the savepoint script as a separate process
        subprocess.run([sys.executable, script_path], check=True)
    except Exception as e:
        print(f"Auto-Save failed: {e}")

def main():
    """The main loop for the Oracle application."""
    task_executor, admin_override, resource_monitor = initialize_oracle()

    # Start the Floating UI
    try:
        ui = OracleUI(task_executor)
        ui.mainloop()
    except Exception as e:
        print(f"Error starting UI: {e}. Falling back to command line interface.")
        # Fallback to command line interface if UI fails
        print("\nOracle is running. Type 'exit' to quit.")
        while True:
            try:
                if admin_override.is_overridden():
                    print("ADMIN OVERRIDE: Oracle is paused or terminated.")
                    break
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break
                response = task_executor.execute_task(user_input)
                print(f"Oracle: {response}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            time.sleep(0.1)
    
    # Trigger Auto-Save before final exit
    trigger_auto_save()

if __name__ == "__main__":
    main()
