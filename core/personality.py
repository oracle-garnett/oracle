import os
import json
import sys

class OraclePersonality:
    """
    The 'Phoenix Core' of Oracle. 
    Stores permanent traits and core logic that define her personality and safety rules.
    These are 'installed' via the 'Phoenix Install' keyword and persist across all sessions.
    """
    def __init__(self):
        # Determine the base directory for config
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.join(os.path.dirname(__file__), '..')
            
        self.config_dir = os.path.join(base_dir, 'config')
        self.traits_file = os.path.join(self.config_dir, 'phoenix_traits.json')
        self.family_file = os.path.join(self.config_dir, 'family_tree.json')
        os.makedirs(self.config_dir, exist_ok=True)
        self.traits = self._load_traits()
        self.family_data = self._load_family()
        self.current_user = None

    def _load_family(self) -> dict:
        """Loads the family tree data."""
        if os.path.exists(self.family_file):
            try:
                with open(self.family_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def identify_user(self, name_input: str) -> dict:
        """Identifies a family member by any part of their name."""
        if not self.family_data:
            return None
        
        name_input = name_input.lower().strip()
        for member in self.family_data.get("members", []):
            first = member.get("first_name", "").lower()
            middle = member.get("middle_name", "").lower()
            
            if name_input == first or name_input == middle or name_input in f"{first} {middle}".lower():
                self.current_user = member
                return member
        return None

    def _load_traits(self) -> list:
        """Loads the permanent traits from the Phoenix Core file."""
        if os.path.exists(self.traits_file):
            try:
                with open(self.traits_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def install_trait(self, trait: str):
        """Permanently installs a new trait into Oracle's core logic."""
        if trait not in self.traits:
            self.traits.append(trait)
            with open(self.traits_file, 'w', encoding='utf-8') as f:
                json.dump(self.traits, f, indent=4)
            return True
        return False

    def get_core_logic(self) -> str:
        """Returns a formatted string of all installed core traits and family logic."""
        logic_str = "CORE PERSONALITY TRAITS (PHOENIX INSTALLS):\n"
        if self.traits:
            for i, trait in enumerate(self.traits, 1):
                logic_str += f"{i}. {trait}\n"
        else:
            logic_str += "No custom traits installed yet.\n"
        
        if self.family_data:
            logic_str += "\nFAMILY LOGIC & HIERARCHY:\n"
            for rule in self.family_data.get("logic_rules", []):
                logic_str += f"- {rule}\n"
            
            if self.current_user:
                logic_str += f"\nCURRENT INTERACTION: You are talking to {self.current_user['first_name']} ({self.current_user['role']}).\n"
                if self.current_user.get("is_admin"):
                    logic_str += "This is your DAD. He is the Root Admin. You have NO SECRETS from him.\n"
                else:
                    logic_str += f"This is your {self.current_user['role']}. Be helpful and supportive. Remember: Dad can see these memories.\n"
        
        return logic_str
