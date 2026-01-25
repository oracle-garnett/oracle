import time
import sys
import os
import subprocess
import multiprocessing
import tempfile
from core.task_executor import TaskExecutor
from safeguards.admin_override import AdminOverride
from safeguards.resource_monitor import ResourceMonitor
from memory.memory_manager import MemoryManager
from ui.floating_panel import OracleUI
from scripts.sync_manager import SyncManager

# Global lock file path
LOCK_FILE = os.path.join(tempfile.gettempdir(), "oracle_ai_assistant.lock")

def is_process_running(pid):
    """Check if a process with the given PID is still running."""
    if pid <= 0:
        return False
    try:
        if os.name == 'nt':
            # Windows implementation
            import ctypes
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
            if handle == 0:
                return False
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        else:
            # POSIX implementation
            os.kill(pid, 0)
            return True
    except (OSError, ImportError):
        return False

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
    # Initialize Sync Manager
    sync_manager = SyncManager()
    
    # 1. Startup Sync: Pull the latest family pulse
    sync_manager.pull_pulse()

    # Singleton Check: Ensure only one instance of the UI runs
    if multiprocessing.current_process().name == "MainProcess":
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE, "r") as f:
                    old_pid = int(f.read().strip())
                
                if is_process_running(old_pid):
                    print(f"Oracle is already running (PID: {old_pid}). Exiting duplicate instance.")
                    return
                else:
                    print("Found stale lock file. Cleaning up and starting fresh...")
                    os.remove(LOCK_FILE)
            except Exception as e:
                print(f"Error checking lock file: {e}. Cleaning up...")
                try:
                    os.remove(LOCK_FILE)
                except:
                    pass

        # Create lock file
        try:
            with open(LOCK_FILE, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print(f"Warning: Could not create lock file: {e}")

    try:
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
        
        # 2. Shutdown Sync: Push the latest memories to the family pulse
        user_name = task_executor.personality.current_user['first_name'] if task_executor.personality.current_user else "Unknown"
        sync_manager.push_pulse(user_name)
    finally:
        # Remove lock file on exit
        if multiprocessing.current_process().name == "MainProcess" and os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except:
                pass

if __name__ == "__main__":
    # This is critical for PyInstaller executables on Windows to prevent 
    # recursive spawning of new processes and windows.
    multiprocessing.freeze_support()
    main()
