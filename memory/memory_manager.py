import os
import json
import time
import sys
from typing import Any, Dict, List
from memory.encryption import MemoryEncryptor
from memory.rag_engine import RAGEngine

class MemoryManager:
    """
    Manages the persistent memory for Oracle.
    Combines local RAG (vector DB) with cloud-based encrypted storage.
    """
    def __init__(self, secret_key: str = None):
        self.encryptor = MemoryEncryptor(secret_key)
        self.rag_engine = RAGEngine()
        self.is_connected = False
        
        # Determine the base directory for logs
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.join(os.path.dirname(__file__), '..')
            
        log_dir = os.path.join(base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        self.local_cache_path = os.path.join(log_dir, 'local_memory.json')
        
        if not os.path.exists(self.local_cache_path):
            with open(self.local_cache_path, 'w') as f:
                json.dump([], f)

    def store_interaction(self, user_input: str, response: str):
        """Stores interaction in both RAG (for retrieval) and encrypted logs."""
        # 1. Add to RAG for semantic search
        memory_text = f"User asked: {user_input} | Oracle replied: {response}"
        self.rag_engine.add_memory(memory_text, metadata={"type": "interaction", "timestamp": time.time()})

        # 2. Encrypt and store in local log
        record = {"timestamp": time.time(), "user_input": user_input, "oracle_response": response}
        encrypted_record = self.encryptor.encrypt(json.dumps(record))
        
        try:
            with open(self.local_cache_path, 'r+') as f:
                data = json.load(f)
                data.append(encrypted_record)
                f.seek(0)
                json.dump(data, f)
        except Exception as e:
            print(f"Error storing memory: {e}")

    def retrieve_memory(self, query: str) -> List[str]:
        """Retrieves relevant memories using the RAG engine."""
        return self.rag_engine.query_memory(query)
