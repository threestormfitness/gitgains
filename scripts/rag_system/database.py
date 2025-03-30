"""
GitGains RAG System Database Module - March 2025
Author: Rob

This module handles all ChromaDB interactions for the GitGains RAG system.
Uses ChromaDB 0.6.3+ for vector storage and semantic search.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import chromadb
from chromadb.config import Settings
from chromadb.api import ClientAPI
from openai import OpenAI

from .config import DEFAULT_CONFIG, RAGConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitGainsDB:
    """
    Database class for GitGains RAG system using ChromaDB 0.6.3+
    """
    def __init__(self, config: RAGConfig = DEFAULT_CONFIG):
        """
        Initialize the database with the given configuration
        """
        self.config = config
        
        # Create persist directory if it doesn't exist
        os.makedirs(self.config.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.config.persist_directory),
            settings=Settings(allow_reset=True)
        )
        
        # Initialize OpenAI client - uses environment variable automatically
        self.openai_client = OpenAI()
        
        # Track collections
        self.collections = {}
        
        logger.info(f"Initialized GitGainsDB with persist directory: {self.config.persist_directory}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using OpenAI's embedding model
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.config.embedding_model
        )
        return response.data[0].embedding
    
    def _get_collection(self, name: str):
        """
        Get or create a collection
        """
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                embedding_function=None  # We'll handle embeddings manually
            )
            logger.info(f"Created/retrieved collection: {name}")
        return self.collections[name]
    
    def add_document(self, collection_name: str, doc_id: str, content: str, metadata: Dict[str, Any]):
        """
        Add a document to a specific collection
        """
        collection = self._get_collection(collection_name)
        
        # Generate embedding
        embedding = self.get_embedding(content)
        
        # Add document
        collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[doc_id]
        )
        logger.info(f"Added document {doc_id} to collection {collection_name}")
    
    def query_collection(
        self, 
        collection_name: str, 
        query_text: str, 
        n_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a specific collection with optional filters
        """
        collection = self._get_collection(collection_name)
        
        # Generate embedding
        query_embedding = self.get_embedding(query_text)
        
        # Execute query
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )
        
        logger.info(f"Queried collection {collection_name} with '{query_text}'")
        return results
    
    def cross_collection_query(
        self, 
        query_text: str, 
        collections: List[str], 
        n_results: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Query multiple collections and combine results
        """
        results = {}
        for collection_name in collections:
            collection_results = self.query_collection(
                collection_name, 
                query_text, 
                n_results
            )
            results[collection_name] = collection_results
        
        logger.info(f"Cross-collection query across {len(collections)} collections")
        return results
    
    def process_json_file(self, json_path: Path, collection_name: str):
        """
        Process a JSON file and add it to the specified collection
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create a unique ID for the document
            doc_id = f"{collection_name}_{json_path.stem}"
            
            # Create document text by combining all string values
            text_fields = []
            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    text_fields.append(f"{key}: {value}")
                elif isinstance(value, (list, dict)):
                    text_fields.append(f"{key}: {json.dumps(value)}")
            
            doc_text = "\n".join(text_fields)
            
            # Add to collection
            self.add_document(
                collection_name=collection_name,
                doc_id=doc_id,
                content=doc_text,
                metadata={
                    "source": str(json_path),
                    "type": "json",
                    "collection": collection_name,
                    **data  # Include all original data as metadata
                }
            )
            logger.info(f"Processed {json_path}")
            return True
        except Exception as e:
            logger.error(f"Error processing {json_path}: {e}")
            return False
    
    def process_markdown_file(self, md_path: Path, collection_name: str):
        """
        Process a Markdown file and add it to the specified collection
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a unique ID for the document
            doc_id = f"{collection_name}_{md_path.stem}"
            
            # Add to collection
            self.add_document(
                collection_name=collection_name,
                doc_id=doc_id,
                content=content,
                metadata={
                    "source": str(md_path),
                    "type": "markdown",
                    "collection": collection_name,
                    "title": md_path.stem
                }
            )
            logger.info(f"Processed {md_path}")
            return True
        except Exception as e:
            logger.error(f"Error processing {md_path}: {e}")
            return False
    
    def load_directory(self, directory: Path, collection_name: str):
        """
        Load all JSON and Markdown files from a directory into a collection
        """
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return
        
        # Process JSON files
        json_count = 0
        for json_file in directory.glob("**/*.json"):
            success = self.process_json_file(json_file, collection_name)
            if success:
                json_count += 1
        
        # Process Markdown files
        md_count = 0
        for md_file in directory.glob("**/*.md"):
            success = self.process_markdown_file(md_file, collection_name)
            if success:
                md_count += 1
        
        logger.info(f"Loaded {json_count} JSON files and {md_count} Markdown files from {directory} into {collection_name}")
    
    def load_all_data(self, data_paths: Dict[str, Path], collections: Dict[str, str]):
        """
        Load all data from the specified paths into their respective collections
        """
        for data_type, path in data_paths.items():
            collection_name = collections.get(data_type, data_type)
            logger.info(f"Loading {data_type} data from {path} into {collection_name}...")
            self.load_directory(path, collection_name)
        
        logger.info("Finished loading all data")
    
    def reset_database(self):
        """
        Reset the database by deleting all collections
        """
        for collection_name in self.collections:
            self.client.delete_collection(collection_name)
        
        self.collections = {}
        logger.info("Reset database - all collections deleted")
    
    def get_collection_metadata(self, collection_name: str) -> Dict:
        """
        Get metadata about a collection
        """
        collection = self._get_collection(collection_name)
        if not collection:
            return {"error": f"Collection {collection_name} not found"}
        
        # Get all documents in the collection
        results = collection.get(include=["metadatas", "documents"])
        
        # Basic stats
        doc_count = len(results["ids"]) if "ids" in results else 0
        
        # Extract metadata fields if available
        metadata_fields = set()
        unique_values = {}
        
        if "metadatas" in results and results["metadatas"]:
            for metadata in results["metadatas"]:
                for key in metadata:
                    metadata_fields.add(key)
                    if key not in unique_values:
                        unique_values[key] = set()
                    unique_values[key].add(metadata[key])
        
        # Convert sets to lists for JSON serialization
        for key in unique_values:
            unique_values[key] = list(unique_values[key])
        
        return {
            "collection_name": collection_name,
            "document_count": doc_count,
            "metadata_fields": list(metadata_fields),
            "unique_values": unique_values
        }
    
    def get_all_collections_metadata(self) -> Dict:
        """
        Get metadata about all collections
        """
        collections_info = {}
        
        for collection_name in self.config.collections:
            collections_info[collection_name] = self.get_collection_metadata(collection_name)
        
        return collections_info
