import os
import json
import time
from typing import Any, Dict, List
from memory.encryption import MemoryEncryptor

class MemoryManager:
    """
    Manages the persistent memory for Oracle.
    Handles cloud database connection and encryption.
    """
    def __init__(self, secret_key: str = None):
        self.encryptor = MemoryEncryptor(secret_key)
        self.db_client = None
        self.is_connected = False
        self.local_cache_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'local_memory.json')
        
        # Ensure local cache exists
        if not os.path.exists(self.local_cache_path):
            with open(self.local_cache_path, 'w') as f:
                json.dump([], f)

    def connect_to_cloud(self, db_type: str, config: Dict[str, Any]):
        """
        Connects to a cloud database (e.g., Supabase, MongoDB Atlas).
        """
        # This will be fully implemented when the user provides their DB credentials
        print(f"Connecting to {db_type} cloud database...")
        self.is_connected = True
        print("Connected to cloud database.")

    def store_interaction(self, user_input: str, response: str):
        """
        Encrypts and stores a user-Oracle interaction.
        """
        record = {
            "timestamp": time.time(),
            "user_input": user_input,
            "oracle_response": response
        }
        
        # 1. Encrypt the record
        record_json = json.dumps(record)
        encrypted_record = self.encryptor.encrypt(record_json)

        # 2. Store in local cache (fallback)
        try:
            with open(self.local_cache_path, 'r+') as f:
                data = json.load(f)
                data.append(encrypted_record)
                f.seek(0)
                json.dump(data, f)
        except Exception as e:
            print(f"Error storing memory locally: {e}")

        # 3. Store in cloud if connected
        if self.is_connected:
            # self.db_client.insert(encrypted_record)
            pass

    def retrieve_memory(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves and decrypts relevant memory fragments.
        """
        # In a full implementation, this would use vector search or keyword search
        # For now, we just return the last few interactions from local cache
        memories = []
        try:
            with open(self.local_cache_path, 'r') as f:
                encrypted_data = json.load(f)
                # Decrypt the last 5 interactions
                for enc_record in encrypted_data[-5:]:
                    dec_record_json = self.encryptor.decrypt(enc_record)
                    memories.append(json.loads(dec_record_json))
        except Exception as e:
            print(f"Error retrieving memory: {e}")
        
        return memories
