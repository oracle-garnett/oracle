import os
import time

class AdminOverride:
    """
    Implements the administrative override and authentication mechanism.
    The user can set a kill switch or pause the system.
    """
    def __init__(self):
        # In a real app, this would be read from a secure config file
        self.admin_pin = "1234" # Placeholder PIN
        self.override_active = False
        print("AdminOverride initialized.")

    def authenticate(self, pin: str) -> bool:
        """Verifies the user's administrative PIN."""
        return pin == self.admin_pin

    def activate_override(self, pin: str) -> bool:
        """Activates the administrative override (e.g., a system pause)."""
        if self.authenticate(pin):
            self.override_active = True
            print("ADMIN OVERRIDE ACTIVATED.")
            return True
        return False

    def deactivate_override(self, pin: str) -> bool:
        """Deactivates the administrative override."""
        if self.authenticate(pin):
            self.override_active = False
            print("ADMIN OVERRIDE DEACTIVATED.")
            return True
        return False

    def is_overridden(self) -> bool:
        """Checks if the system is currently under administrative override."""
        # In a real app, this could also check for a signal file or a network flag
        return self.override_active
