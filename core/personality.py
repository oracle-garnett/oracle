import os
import json

class OraclePersonality:
    """
    The 'Phoenix Core' of Oracle. 
    Stores permanent traits and core logic that define her personality and safety rules.
    These are 'installed' via the 'Phoenix Install' keyword and persist across all sessions.
    """
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.traits_file = os.path.join(self.config_dir, 'phoenix_traits.json')
        os.makedirs(self.config_dir, exist_ok=True)
        self.traits = self._load_traits()

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
        """Returns a formatted string of all installed core traits for the system prompt."""
        if not self.traits:
            return "No core traits installed yet."
        
        logic_str = "CORE PERSONALITY TRAITS (PHOENIX INSTALLS):\n"
        for i, trait in enumerate(self.traits, 1):
            logic_str += f"{i}. {trait}\n"
        return logic_str
