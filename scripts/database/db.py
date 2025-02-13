import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from models import LoadingModule, DatabaseConfig

class GitGainsDB:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client = chromadb.PersistentClient(
            path=config.persist_directory,
            settings=Settings(allow_reset=True)
        )
        
        # Initialize embedding function
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config.embedding_function
        )
        
        # Track collections
        self.collections = {}
        
    def get_collection(self, name: str):
        """Get or create a collection"""
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                embedding_function=self.ef
            )
        return self.collections[name]
    
    def add_document(self, collection_name: str, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Add a document to a specific collection"""
        collection = self.get_collection(collection_name)
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
    
    def query_collection(self, collection_name: str, query_text: str, n_results: int = 5,
                        filter_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query a specific collection with optional filters"""
        collection = self.get_collection(collection_name)
        return collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=filter_dict
        )
    
    def cross_collection_query(self, query_text: str, collections: List[str], 
                             n_results: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Query multiple collections and combine results"""
        results = {}
        for collection_name in collections:
            collection_results = self.query_collection(collection_name, query_text, n_results)
            results[collection_name] = collection_results
        return results
    
    def process_json_file(self, json_path: Path, collection_name: str):
        """Process any JSON file and add it to the specified collection"""
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Normalize data while preserving original values
        from normalizers import normalize_module_data
        normalized_data = normalize_module_data(data)
            
        # Create document text combining important text fields
        text_fields = [str(v) for v in normalized_data.values() if isinstance(v, (str, int, float))]
        doc_text = "\n".join(text_fields)
        
        # Add to collection
        self.add_document(
            collection_name=collection_name,
            doc_id=normalized_data.get('id', json_path.stem),
            content=doc_text,
            metadata=normalized_data
        )
    
    def load_directory(self, directory: Path, collection_name: str):
        """Load all JSON files from a directory into a collection"""
        for json_file in directory.glob("**/*.json"):
            print(f"Processing {json_file.name} into {collection_name}...")
            self.process_json_file(json_file, collection_name)
