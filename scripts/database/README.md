# GitGains Database

This directory contains the database implementation for GitGains, using Chroma as a vector database to store and query training modules.

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Loading Data
Run the data loader to populate the database:
```bash
python load_data.py
```

### Using the Database
Example Python code to query the database:

```python
from models import DatabaseConfig
from db import GitGainsDB

# Initialize database
config = DatabaseConfig()
db = GitGainsDB(config)

# Query similar modules
results = db.query("high intensity cluster sets for strength")

# Get specific module
module = db.get_by_id("cluster_90pct_1rm_12min")
```

## Structure

- `models.py`: Pydantic models for data validation
- `db.py`: Main database implementation
- `load_data.py`: Script to load data into the database

## Features

- Local vector database using Chroma
- Combines JSON data with markdown documentation
- Flexible schema that can evolve over time
- Semantic search capabilities
- Easy to extend for new module types
