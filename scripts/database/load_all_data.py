from pathlib import Path
from models import DatabaseConfig
from db import GitGainsDB

def main():
    # Initialize database
    db = GitGainsDB(DatabaseConfig(persist_directory="../../data/db"))
    
    # Base data directory
    data_dir = Path("../../data")
    
    # Load each type of data into its own collection
    collections = {
        "loading_modules": data_dir / "loading_modules",
        "exercise_substitutions": data_dir / "exercise_substitutions",
        "program_parameters": data_dir / "program_parameters",
    }
    
    for collection_name, directory in collections.items():
        if directory.exists():
            print(f"\nLoading {collection_name}...")
            db.load_directory(directory, collection_name)

if __name__ == "__main__":
    main()
