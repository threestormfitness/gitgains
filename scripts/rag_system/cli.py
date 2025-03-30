"""
GitGains RAG System CLI - March 2025
Author: Rob

Command-line interface for the GitGains RAG system.
Provides commands for indexing data, querying, and managing the database.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

from .config import DEFAULT_CONFIG, RAGConfig, DATA_PATHS, COLLECTIONS
from .database import GitGainsDB
from .query_engine import QueryEngine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gitgains_rag.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set up rich console
console = Console()

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
def cli(debug):
    """GitGains RAG System - Fitness Programming Assistant"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

@cli.command()
@click.option('--reset/--no-reset', default=False, help='Reset the database before indexing')
@click.option('--collection', '-c', multiple=True, help='Specific collection(s) to index')
def index(reset, collection):
    """Index data into the ChromaDB database"""
    with Progress() as progress:
        task = progress.add_task("[green]Indexing data...", total=len(DATA_PATHS))
        
        # Initialize database
        db = GitGainsDB(DEFAULT_CONFIG)
        
        if reset:
            console.print("[bold red]Resetting database...[/bold red]")
            db.reset_database()
        
        # Filter collections if specified
        if collection:
            data_paths = {k: v for k, v in DATA_PATHS.items() if k in collection}
            collections = {k: v for k, v in COLLECTIONS.items() if k in collection}
        else:
            data_paths = DATA_PATHS
            collections = COLLECTIONS
        
        # Index data
        console.print("[bold]Indexing data into ChromaDB...[/bold]")
        
        for data_type, path in data_paths.items():
            collection_name = collections.get(data_type, data_type)
            console.print(f"Indexing {data_type} from {path}...")
            db.load_directory(path, collection_name)
            progress.update(task, advance=1)
        
        console.print("[bold green]✓ Indexing complete![/bold green]")

@cli.command()
@click.argument('query', nargs=-1)
@click.option('--collection', '-c', multiple=True, help='Specific collection(s) to query')
@click.option('--results', '-n', default=3, help='Number of results per collection')
@click.option('--show-context/--no-show-context', default=False, help='Show retrieved context')
def query(query, collection, results, show_context):
    """Query the RAG system with a question"""
    query_text = ' '.join(query)
    
    if not query_text:
        console.print("[bold red]Error: Query text is required[/bold red]")
        return
    
    # Initialize components
    db = GitGainsDB(DEFAULT_CONFIG)
    query_engine = QueryEngine(db, DEFAULT_CONFIG)
    
    # Convert collection names to actual collection IDs
    collection_ids = None
    if collection:
        collection_ids = [COLLECTIONS.get(c, c) for c in collection]
    
    with Progress() as progress:
        # Retrieve context
        context_task = progress.add_task("[green]Retrieving context...", total=1)
        context = query_engine.retrieve_context(
            query=query_text,
            collections=collection_ids,
            n_results=results
        )
        progress.update(context_task, completed=1)
        
        # Show context if requested
        if show_context:
            console.print(Panel(context, title="[bold]Retrieved Context[/bold]", 
                               border_style="blue", expand=False))
        
        # Generate response
        response_task = progress.add_task("[green]Generating response...", total=1)
        response = query_engine.generate_response(
            query=query_text,
            context=context
        )
        progress.update(response_task, completed=1)
    
    # Display response
    console.print(Panel(Markdown(response), title=f"[bold]Response to: {query_text}[/bold]", 
                       border_style="green", expand=False))

@cli.command()
def interactive():
    """Start an interactive session with the RAG system"""
    # Initialize components
    db = GitGainsDB(DEFAULT_CONFIG)
    query_engine = QueryEngine(db, DEFAULT_CONFIG)
    
    console.print(Panel(
        "[bold]GitGains Interactive RAG System[/bold]\n\n"
        "Type your questions about fitness programming, or use these special commands:\n"
        "- [bold]/collections[/bold] - List available collections\n"
        "- [bold]/filter [collection names][/bold] - Filter to specific collections\n"
        "- [bold]/reset[/bold] - Reset collection filters\n"
        "- [bold]/exit[/bold] - Exit the interactive session",
        title="Welcome",
        border_style="green"
    ))
    
    # Track active collections
    active_collections = None
    
    while True:
        # Show active collections if filtered
        if active_collections:
            collection_str = ", ".join(active_collections)
            console.print(f"[bold blue]Active collections:[/bold blue] {collection_str}")
        
        # Get user input
        user_input = console.input("[bold green]Ask a question:[/bold green] ")
        
        # Handle special commands
        if user_input.lower() == "/exit":
            console.print("[bold]Goodbye![/bold]")
            break
        
        elif user_input.lower() == "/collections":
            console.print(Panel(
                "\n".join(f"- [bold]{k}[/bold]: {v}" for k, v in COLLECTIONS.items()),
                title="Available Collections",
                border_style="blue"
            ))
            continue
        
        elif user_input.lower() == "/reset":
            active_collections = None
            console.print("[bold blue]Reset collection filters[/bold blue]")
            continue
        
        elif user_input.lower().startswith("/filter"):
            parts = user_input.split()
            if len(parts) > 1:
                collections = parts[1:]
                active_collections = [COLLECTIONS.get(c, c) for c in collections if c in COLLECTIONS]
                console.print(f"[bold blue]Filtered to collections:[/bold blue] {', '.join(active_collections)}")
            else:
                console.print("[bold red]Error: Specify collections to filter[/bold red]")
            continue
        
        # Process regular query
        with Progress() as progress:
            # Retrieve context
            context_task = progress.add_task("[green]Retrieving context...", total=1)
            context = query_engine.retrieve_context(
                query=user_input,
                collections=active_collections
            )
            progress.update(context_task, completed=1)
            
            # Generate response
            response_task = progress.add_task("[green]Generating response...", total=1)
            response = query_engine.generate_response(
                query=user_input,
                context=context
            )
            progress.update(response_task, completed=1)
        
        # Display response
        console.print(Panel(Markdown(response), border_style="green", expand=False))

@cli.command()
def info():
    """Show information about the RAG system configuration"""
    db = GitGainsDB(DEFAULT_CONFIG)
    
    # Get collection information
    collection_info = []
    for collection_name in COLLECTIONS.values():
        try:
            collection = db.get_collection(collection_name)
            count = collection.count()
            collection_info.append((collection_name, count))
        except Exception as e:
            collection_info.append((collection_name, f"Error: {str(e)}"))
    
    # Display configuration
    console.print(Panel(
        "[bold]Database Configuration[/bold]\n"
        f"Persist Directory: {DEFAULT_CONFIG.persist_directory}\n"
        f"Embedding Model: {DEFAULT_CONFIG.embedding_model}\n"
        f"OpenAI Model: {DEFAULT_CONFIG.openai_model}\n"
        f"Max Tokens Per Chunk: {DEFAULT_CONFIG.max_tokens_per_chunk}\n"
        f"Max Total Tokens: {DEFAULT_CONFIG.max_total_tokens}\n\n"
        "[bold]Collections[/bold]\n" +
        "\n".join(f"- {name}: {count} documents" for name, count in collection_info),
        title="GitGains RAG System Info",
        border_style="blue"
    ))

@cli.command()
def metadata():
    """
    Display metadata about the collections in the database
    """
    rich_console = Console()
    
    # Initialize database
    db = GitGainsDB(config=DEFAULT_CONFIG)
    
    # Get metadata for all collections
    metadata = db.get_all_collections_metadata()
    
    # Display metadata in a nice format
    rich_console.print("\n[bold]GitGains Database Metadata[/bold]\n", style="green")
    
    for collection_name, collection_data in metadata.items():
        doc_count = collection_data.get("document_count", 0)
        
        # Create a panel for each collection
        rich_console.print(f"[bold]{collection_name}[/bold]: {doc_count} documents", style="blue")
        
        # Display metadata fields if available
        metadata_fields = collection_data.get("metadata_fields", [])
        if metadata_fields:
            rich_console.print("  [bold]Metadata fields:[/bold]", style="yellow")
            for field in metadata_fields:
                rich_console.print(f"    - {field}")
            
            # Display some statistics about unique values
            unique_values = collection_data.get("unique_values", {})
            for field, values in unique_values.items():
                if len(values) < 20:  # Only show if not too many values
                    rich_console.print(f"    [bold]{field}[/bold] has {len(values)} unique values: {', '.join(str(v) for v in values[:5])}{' ...' if len(values) > 5 else ''}")
                else:
                    rich_console.print(f"    [bold]{field}[/bold] has {len(values)} unique values")
        
        rich_console.print("")  # Add a blank line between collections

if __name__ == "__main__":
    cli()
