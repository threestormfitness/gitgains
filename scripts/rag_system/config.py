"""
GitGains RAG System Configuration - March 2025
Author: Rob

This file contains configuration settings for the GitGains RAG system.
"""

import os
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Optional, Union

# Base directories
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = ROOT_DIR / "data"
DB_DIR = ROOT_DIR / "scripts" / "rag_system" / "db"

# Data directories
DATA_PATHS = {
    "loading_modules": DATA_DIR / "loading_modules",
    "movements": DATA_DIR / "movements",
    "master_lists": DATA_DIR / "master_lists",
    "programs": DATA_DIR / "programs",
    "exercise_substitutions": DATA_DIR / "exercise_substitutions",
    "program_parameters": DATA_DIR / "program_parameters",
}

# Collection names
COLLECTIONS = {
    "loading_modules": "loading_modules",
    "movements": "movements",
    "master_lists": "master_lists", 
    "programs": "programs",
    "exercise_substitutions": "exercise_substitutions",
    "program_parameters": "program_parameters",
}

class RAGConfig(BaseModel):
    """Configuration for the RAG system"""
    # Database settings
    persist_directory: Path = DB_DIR
    collections: Dict[str, str] = COLLECTIONS
    
    # Embedding settings
    embedding_model: str = "text-embedding-3-small"
    
    # OpenAI settings
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    
    # Token management
    max_tokens_per_chunk: int = 1000
    max_total_tokens: int = 6000
    
    # CLI settings
    default_num_results: int = 5

    class Config:
        arbitrary_types_allowed = True

# Default configuration
DEFAULT_CONFIG = RAGConfig()
