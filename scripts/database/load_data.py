import os
from pathlib import Path

from models import DatabaseConfig
from db import GitGainsDB

def main():
    # Configure database
    config = DatabaseConfig(
        persist_directory="../../data/db",
        collection_name="loading_modules",
        embedding_function="all-MiniLM-L6-v2"
    )
    
    # Initialize database
    db = GitGainsDB(config)
    
    # Process all loading modules
    modules_dir = Path("../../data/loading_modules")
    for json_file in modules_dir.glob("*.json"):
        print(f"Processing {json_file.name}...")
        module = db.process_loading_module(json_file)
        db.add_loading_module(module)
        print(f"Added {module.name} to database")

if __name__ == "__main__":
    main()
