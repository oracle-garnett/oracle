import subprocess
import sys
import os

def run_skill_test(skill_file_path):
    """
    Runs a basic test on a newly created skill file to ensure it doesn't crash.
    """
    try:
        # Run the script in a separate process to avoid crashing the main app
        result = subprocess.run([sys.executable, skill_file_path], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "Test passed!"
        else:
            return False, f"Test failed with error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Test timed out (possible infinite loop)."
    except Exception as e:
        return False, f"An error occurred during testing: {e}"
