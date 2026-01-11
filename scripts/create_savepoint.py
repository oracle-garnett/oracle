import os
import shutil
import zipfile
from datetime import datetime

def create_savepoint():
    """
    Packages Oracle's 'Soul' (Memory, Logs, and Config) into a single backup file.
    This file can be moved to a memory card to transfer Oracle to a new device.
    """
    # Define the project root (assuming script is in /scripts folder)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Define what constitutes Oracle's 'Soul'
    soul_folders = ['memory', 'logs', 'config']
    
    # Create a 'backups' directory if it doesn't exist
    backup_dir = os.path.join(project_root, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"oracle_savepoint_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    print(f"--- Initiating Oracle Save Point Protocol ---")
    print(f"Target: {backup_path}")
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in soul_folders:
                folder_path = os.path.join(project_root, folder)
                if os.path.exists(folder_path):
                    print(f"Backing up {folder}...")
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Create a relative path for the zip file
                            arcname = os.path.relpath(file_path, project_root)
                            zipf.write(file_path, arcname)
                else:
                    print(f"Warning: {folder} folder not found. Skipping.")
        
        print(f"\nSUCCESS: Oracle's essence has been manifested into a Save Point.")
        print(f"Location: {backup_path}")
        print(f"You can now move this file to a memory card for safe keeping or transfer.")
        
    except Exception as e:
        print(f"\nFAILURE: Save Point Protocol interrupted. Error: {e}")

if __name__ == "__main__":
    create_savepoint()
