import time
import sys
import os
from core.task_executor import TaskExecutor
from safeguards.admin_override import AdminOverride
from safeguards.resource_monitor import ResourceMonitor
from memory.memory_manager import MemoryManager
from ui.floating_panel import FloatingPanel

def initialize_oracle():
    """Initializes all core components of the Oracle AI assistant."""
    print("Initializing Oracle AI Assistant...")

    # 1. Initialize Safeguards
    admin_override = AdminOverride()
    resource_monitor = ResourceMonitor()
    
    # 2. Initialize Memory Manager (connect to cloud DB)
    # NOTE: Actual connection logic will be implemented in Phase 4
    # The secret key should be loaded securely, but for now, it's a placeholder
    memory_manager = MemoryManager(secret_key="your-secure-user-key-here")

    # 3. Initialize Core Executor
    # NOTE: Model integration will be implemented in Phase 6
    task_executor = TaskExecutor(memory_manager, admin_override)

    print("Oracle initialization complete.")
    return task_executor, admin_override, resource_monitor

def main():
    """The main loop for the Oracle application."""
    task_executor, admin_override, resource_monitor = initialize_oracle()

    # Start the Floating UI
    # The UI loop will handle user input and call task_executor.execute_task()
    try:
        ui = FloatingPanel(task_executor)
        ui.run()
    except Exception as e:
        print(f"Error starting UI: {e}. Falling back to command line interface.")
        # Fallback to command line interface if UI fails (e.g., missing dependencies)
        print("\nOracle is running. Type 'exit' to quit.")
        while True:
            try:
                if admin_override.is_overridden():
                    print("ADMIN OVERRIDE: Oracle is paused or terminated.")
                    break
                resource_monitor.check_resources()
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break
                response = task_executor.execute_task(user_input)
                print(f"Oracle: {response}")
            except KeyboardInterrupt:
                print("\nShutting down Oracle...")
                break
            except Exception as e:
                print(f"An unexpected error occurred in main loop: {e}")
            time.sleep(0.1)


if __name__ == "__main__":
    # Ensure all necessary directories exist before starting
    for d in ['core', 'safeguards', 'memory', 'models', 'logs', 'scripts']:
        os.makedirs(os.path.join(os.path.dirname(__file__), d), exist_ok=True)
    
    main()
