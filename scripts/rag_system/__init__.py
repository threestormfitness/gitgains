"""
GitGains RAG System - March 2025
Author: Rob

A Retrieval-Augmented Generation (RAG) system for intelligent workout programming.
Uses ChromaDB 0.6.3+ and OpenAI 1.68.2+ for semantic search and AI-powered responses.
"""

from .config import RAGConfig, DEFAULT_CONFIG
from .database import GitGainsDB
from .query_engine import QueryEngine

__version__ = "1.0.0"
