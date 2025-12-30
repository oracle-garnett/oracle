"""
Encryption module for Oracle's memory persistence.

This module provides functions to encrypt and decrypt data before it is stored
in the cloud database, ensuring user privacy.
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class MemoryEncryptor:
    """
    Handles encryption and decryption of memory records.
    """
    def __init__(self, secret_key: str = None):
        if secret_key is None:
            # In a real app, this would be a user-provided password or a machine-specific key
            secret_key = "oracle-default-secret-key"
        
        self.key = self._generate_key(secret_key)
        self.fernet = Fernet(self.key)

    def _generate_key(self, password: str) -> bytes:
        """Generates a cryptographic key from a password."""
        password_bytes = password.encode()
        salt = b'oracle_salt_' # In a real app, use a unique salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key

    def encrypt(self, data: str) -> str:
        """Encrypts a string and returns the base64 encoded ciphertext."""
        encrypted_data = self.fernet.encrypt(data.encode())
        return encrypted_data.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts a base64 encoded ciphertext and returns the original string."""
        decrypted_data = self.fernet.decrypt(ciphertext.encode())
        return decrypted_data.decode()
