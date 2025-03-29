# GitGains RAG System

A robust Retrieval-Augmented Generation (RAG) system for intelligent workout programming, built with ChromaDB and OpenAI.

## Overview

GitGains RAG System is a command-line tool that enables semantic search across structured training data and generates evidence-based fitness programming responses using OpenAI's GPT-4o model.

### Key Features

- **Efficient Data Indexing**: Indexes JSON and Markdown files from multiple data directories
- **Semantic Search**: Uses ChromaDB 0.6.3+ for vector storage and semantic search
- **Token Optimization**: Intelligently manages context size for optimal OpenAI API usage
- **Flexible Querying**: Query specific collections or search across all data
- **Interactive CLI**: User-friendly command-line interface with rich formatting

## Installation

### Prerequisites

- Python 3.10+
- Microsoft Visual C++ Build Tools (for ChromaDB)
- OpenAI API key (as an environment variable or in a .env file)

### Setup

1. Clone the repository (if you haven't already)
2. Navigate to the GitGains directory
3. Create a virtual environment:
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # On Windows
   ```
4. Install dependencies:
   ```
   cd scripts/rag_system
   pip install -r requirements.txt
   ```
5. **API Key Setup** (choose one option):
   - **Option A**: The system will automatically use your OPENAI_API_KEY environment variable if it's already set
   - **Option B**: Create a `.env` file in the `scripts/rag_system` directory:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

The RAG system provides several commands through its CLI:

### Indexing Data

Before querying, you need to index your data into ChromaDB:

```
python -m scripts.rag_system.cli index
```

Options:
- `--reset`: Reset the database before indexing
- `--collection/-c`: Specify specific collection(s) to index

### Querying

Query the system with a question:

```
python -m scripts.rag_system.cli query "Create a 4-week intermediate deadlift program"
```

Options:
- `--collection/-c`: Specify specific collection(s) to query
- `--results/-n`: Number of results per collection (default: 3)
- `--show-context`: Show the retrieved context used for the response

### Interactive Mode

Start an interactive session:

```
python -m scripts.rag_system.cli interactive
```

Special commands in interactive mode:
- `/collections`: List available collections
- `/filter [collection names]`: Filter to specific collections
- `/reset`: Reset collection filters
- `/exit`: Exit the interactive session

### System Information

View information about the RAG system configuration:

```
python -m scripts.rag_system.cli info
```

## Architecture

The GitGains RAG system consists of several components:

1. **Database Module** (`database.py`): Handles ChromaDB interactions for storing and retrieving vectors
2. **Query Engine** (`query_engine.py`): Processes queries, retrieves context, and generates responses
3. **Configuration** (`config.py`): Manages system settings and paths
4. **CLI Interface** (`cli.py`): Provides a command-line interface for interacting with the system

## Scaling

The system is designed to scale as your data grows:

- Uses efficient embedding models to minimize token usage
- Implements context optimization to stay within token limits
- Supports filtering by collection to focus on relevant data
- Persistent database storage for fast retrieval

## Library Versions

- ChromaDB: 0.6.3+
- OpenAI: 1.68.2+
- Pydantic: 1.10.8+
- Tiktoken: 0.5.2+
- Click: 8.1.7+
- Rich: 13.7.1+
- Sentence-Transformers: 2.6.0+

## License

This project is licensed under the terms of the license included with the GitGains repository.
