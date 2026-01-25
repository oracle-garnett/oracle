import subprocess
import os
import sys
import time

class SyncManager:
    """
    Handles the 'Family Pulse' sync logic.
    Automatically pulls updates on startup and pushes on shutdown via Git.
    """
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.join(os.path.dirname(__file__), '..')
        
        self.repo_dir = os.path.abspath(self.base_dir)

    def _run_git(self, args):
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def pull_pulse(self):
        """Pulls the latest family memory and traits from GitHub."""
        print("Oracle is checking for family updates...")
        # Fetch and merge changes
        success, output = self._run_git(['pull', 'origin', 'main', '--rebase'])
        if success:
            print("Sync Complete: Oracle is now up to date with the family.")
        else:
            print(f"Sync Warning: Could not reach the family pulse. {output}")
        return success

    def push_pulse(self, user_name="Unknown"):
        """Pushes the latest interactions and traits to GitHub."""
        print(f"Oracle is saving her memories for the family...")
        
        # Add logs, config, and memory files
        files_to_sync = ['logs/', 'config/', 'memory/']
        for folder in files_to_sync:
            self._run_git(['add', folder])
        
        # Commit with a timestamp and user info
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Family Pulse Sync: {user_name} at {timestamp}"
        
        success, _ = self._run_git(['commit', '-m', commit_msg])
        if not success:
            # Likely nothing to commit
            return True
            
        success, output = self._run_git(['push', 'origin', 'main'])
        if success:
            print("Sync Complete: Memories safely stored in the family pulse.")
        else:
            print(f"Sync Warning: Could not push to the family pulse. {output}")
        return success

if __name__ == "__main__":
    # Simple CLI for testing
    sync = SyncManager()
    if len(sys.argv) > 1:
        if sys.argv[1] == "pull":
            sync.pull_pulse()
        elif sys.argv[1] == "push":
            user = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
            sync.push_pulse(user)
