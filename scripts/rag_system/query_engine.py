"""
GitGains RAG System Query Engine - March 2025
Author: Rob

This module handles query processing, context retrieval, and formatting for the OpenAI API.
Optimizes token usage and ensures efficient context management.
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any

from openai import OpenAI
from .config import DEFAULT_CONFIG, RAGConfig
from .database import GitGainsDB

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryEngine:
    """
    Query engine for GitGains RAG system
    Handles retrieval and formatting of context for OpenAI
    """
    def __init__(self, db: GitGainsDB, config: RAGConfig = DEFAULT_CONFIG):
        """
        Initialize the query engine with the given database and configuration
        """
        self.db = db
        self.config = config
        self.openai_client = OpenAI()
        
        logger.info(f"Initialized QueryEngine with model: {self.config.openai_model}")
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string
        Simple approximation: ~4 characters per token for English text
        """
        return len(text) // 4
    
    def truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to stay within token limit (estimated)
        """
        estimated_tokens = self.count_tokens(text)
        if estimated_tokens <= max_tokens:
            return text
        
        # Simple truncation based on character count
        char_limit = max_tokens * 4
        return text[:char_limit] + "..."
    
    def format_document(self, document: str, metadata: Dict[str, Any]) -> str:
        """
        Format a document with its metadata for inclusion in context
        """
        # Extract key metadata fields
        source = metadata.get("source", "Unknown")
        doc_type = metadata.get("type", "Unknown")
        collection = metadata.get("collection", "Unknown")
        
        # Format header
        header = f"SOURCE: {source}\nTYPE: {doc_type}\nCOLLECTION: {collection}\n\n"
        
        # Format content
        formatted_doc = f"{header}{document}"
        
        # Truncate if needed
        if self.count_tokens(formatted_doc) > self.config.max_tokens_per_chunk:
            formatted_doc = self.truncate_to_token_limit(
                formatted_doc, 
                self.config.max_tokens_per_chunk
            )
            formatted_doc += "\n[Document truncated due to token limit]"
        
        return formatted_doc
    
    def format_query_results(self, results: Dict[str, Any], collection_name: str) -> List[str]:
        """
        Format query results from a single collection
        """
        formatted_docs = []
        
        if not results or "documents" not in results:
            return formatted_docs
        
        documents = results["documents"][0]  # First query result set
        metadatas = results["metadatas"][0]  # First query result set
        
        for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
            formatted_doc = self.format_document(doc, metadata)
            formatted_docs.append(formatted_doc)
        
        return formatted_docs
    
    def optimize_context(self, formatted_docs: List[str], max_tokens: int) -> str:
        """
        Optimize context to stay within token limit
        """
        total_tokens = 0
        selected_docs = []
        
        for doc in formatted_docs:
            doc_tokens = self.count_tokens(doc)
            
            if total_tokens + doc_tokens <= max_tokens:
                selected_docs.append(doc)
                total_tokens += doc_tokens
            else:
                # If we can't fit the whole document, try to fit a truncated version
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only if we have enough tokens left
                    truncated_doc = self.truncate_to_token_limit(doc, remaining_tokens)
                    selected_docs.append(truncated_doc + "\n[Document truncated due to token limit]")
                break
        
        return "\n\n---\n\n".join(selected_docs)
    
    def query_single_collection(
        self, 
        query: str, 
        collection_name: str, 
        n_results: int = None
    ) -> List[str]:
        """
        Query a single collection and format the results
        """
        n_results = n_results or self.config.default_num_results
        
        results = self.db.query_collection(
            collection_name=collection_name,
            query_text=query,
            n_results=n_results
        )
        
        formatted_docs = self.format_query_results(results, collection_name)
        return formatted_docs
    
    def query_all_collections(
        self, 
        query: str, 
        n_results_per_collection: int = None
    ) -> List[str]:
        """
        Query all collections and format the results
        """
        n_results = n_results_per_collection or self.config.default_num_results
        all_formatted_docs = []
        
        for collection_name in self.config.collections.values():
            formatted_docs = self.query_single_collection(
                query=query,
                collection_name=collection_name,
                n_results=n_results
            )
            all_formatted_docs.extend(formatted_docs)
        
        return all_formatted_docs
    
    def retrieve_context(
        self, 
        query: str, 
        collections: Optional[List[str]] = None, 
        n_results: int = None
    ) -> str:
        """
        Retrieve and format context for a query
        """
        n_results = n_results or self.config.default_num_results
        
        if collections:
            # Query specific collections
            all_formatted_docs = []
            for collection_name in collections:
                formatted_docs = self.query_single_collection(
                    query=query,
                    collection_name=collection_name,
                    n_results=n_results
                )
                all_formatted_docs.extend(formatted_docs)
        else:
            # Query all collections
            all_formatted_docs = self.query_all_collections(
                query=query,
                n_results_per_collection=n_results
            )
        
        # Optimize context to stay within token limit
        optimized_context = self.optimize_context(
            all_formatted_docs,
            self.config.max_total_tokens
        )
        
        return optimized_context
    
    def generate_response(
        self, 
        query: str, 
        context: str, 
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response using OpenAI with the given query and context
        """
        default_system_prompt = """
        You are GitGains AI, a fitness programming assistant that specializes in creating 
        evidence-based resistance training programs. Use the provided context to answer 
        questions about workout programming, loading modules, exercise selection, and 
        periodization strategies. If the information isn't in the context, say so rather 
        than making things up.
        
        Provide detailed, comprehensive answers that thoroughly explain concepts and include
        practical examples. Don't be afraid to write lengthy responses when the question
        warrants in-depth explanation. Include scientific reasoning and evidence where relevant.
        
        When creating workout programs, include detailed progression strategies, exercise
        variations, and specific implementation guidelines. Make your answers actionable
        and educational.
        """
        
        system_prompt = system_prompt or default_system_prompt
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        response = self.openai_client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            temperature=self.config.openai_temperature,
            max_tokens=2000  # Increased max tokens for more detailed responses
        )
        
        return response.choices[0].message.content
    
    def query_and_respond(
        self, 
        query: str, 
        collections: Optional[List[str]] = None, 
        n_results: int = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        End-to-end query processing: retrieve context and generate response
        """
        # Retrieve context
        context = self.retrieve_context(
            query=query,
            collections=collections,
            n_results=n_results
        )
        
        # Generate response
        response = self.generate_response(
            query=query,
            context=context,
            system_prompt=system_prompt
        )
        
        return response
