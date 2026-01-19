"""
RAG (Retrieval-Augmented Generation) Engine for Oracle.

This module manages the vector database and retrieval logic, allowing Oracle
to have a persistent, evolving memory.
"""

import os
import json
import sys
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

class RAGEngine:
    """
    Manages the local vector database for long-term memory retrieval.
    """
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # Determine the base directory for logs
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.join(os.path.dirname(__file__), '..')
                
            storage_path = os.path.join(base_dir, 'logs', 'vector_db')
        
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=storage_path)
        
        # Use a lightweight embedding function (runs locally)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create the 'oracle_memory' collection
        self.collection = self.client.get_or_create_collection(
            name="oracle_memory",
            embedding_function=self.embedding_fn
        )

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        """Adds a new piece of information to Oracle's long-term memory."""
        # Generate a unique ID based on timestamp
        memory_id = f"mem_{int(time.time() * 1000)}"
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[memory_id]
        )

    def query_memory(self, query_text: str, n_results: int = 3) -> List[str]:
        """Retrieves the most relevant memories for a given query."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Return the documents (the actual text of the memories)
        return results['documents'][0] if results['documents'] else []

# Import time for ID generation
import time
