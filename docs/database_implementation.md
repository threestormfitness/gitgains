# GitGains Database Implementation Guide

## Overview
This document explains the vector database implementation for GitGains, which allows flexible storage and AI-friendly querying of training modules, exercise substitutions, and programming parameters.

## Key Features
- Local vector database using Chroma
- Flexible schema that handles varying data formats
- Automatic normalization while preserving original data
- AI-ready for program generation
- Easy to extend with new data types

## Directory Structure
```
gitgains/
├── scripts/
│   └── database/
│       ├── requirements.txt    # Python dependencies
│       ├── models.py          # Data models and validation
│       ├── db.py             # Main database implementation
│       ├── normalizers.py    # Data standardization
│       ├── load_data.py      # Single collection loader
│       └── load_all_data.py  # Multi-collection loader
├── data/
│   ├── db/                   # Where Chroma stores data
│   ├── loading_modules/      # Your JSON/MD files
│   ├── exercise_substitutions/
│   └── program_parameters/
```

## Getting Started

### 1. Initial Setup
```bash
cd scripts/database
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Load Your Data
```bash
# Load all collections
python load_all_data.py

# Or load just loading modules
python load_data.py
```

## How It Works

### 1. Data Models (`models.py`)
- Defines Pydantic models for data validation
- Flexible schema allows additional fields
- Handles both strict and loose data types

### 2. Database Implementation (`db.py`)
- Manages Chroma collections
- Handles document storage and retrieval
- Supports cross-collection queries
- Integrates with normalizers

### 3. Data Normalization (`normalizers.py`)
- Standardizes data while preserving original format
- Adds normalized fields with `_normalized` suffix
- Currently handles:
  - Time values (converts to minutes)
  - Load/intensity values (converts to percentages)
  - Easy to add new normalizers

### 4. Program Generation (`program_generator.py`)
- Integrates with OpenAI's GPT-4
- Uses your data to create informed programs
- Considers time constraints and exercise selection
- References your loading modules

## Working with Data

### Adding New Data
1. Create JSON files in appropriate directories
2. Run `load_all_data.py` to update database
3. No need to modify existing files

### Modifying Data Structure
- Add new fields to JSON files anytime
- No database schema updates needed
- Normalizers handle varying formats

### Querying Examples

1. **Simple Query**
```python
from models import DatabaseConfig
from db import GitGainsDB

db = GitGainsDB(DatabaseConfig())
results = db.query_collection(
    "loading_modules",
    "Find high-intensity cluster sets"
)
```

2. **Using Normalized Values**
```python
# Find modules that take 8-12 minutes
results = db.query_collection(
    "loading_modules",
    "Find modules around 10 minutes",
    filter_dict={
        "avg_time_session_normalized": {
            "$gte": 8,
            "$lte": 12
        }
    }
)
```

3. **Cross-Collection Query**
```python
# Find related modules and substitutions
results = db.cross_collection_query(
    "bench press variations for shoulder health",
    collections=["loading_modules", "exercise_substitutions"]
)
```

## AI Integration

### Using with OpenAI
1. Create `.env` file with your API key:
```
OPENAI_API_KEY=your_key_here
```

2. Generate programs:
```python
from program_generator import ProgramGenerator

generator = ProgramGenerator()
program = generator.generate_program(
    "Create a 3-day full body program..."
)
```

## Data Organization Best Practices

### Loading Modules
- Keep JSON and MD files together
- Use consistent naming patterns
- Include source material when available

### Exercise Substitutions
- Organize by movement pattern
- Include rationale and constraints
- Cross-reference with loading modules

### Program Parameters
- Separate by type (periodization, progression, etc.)
- Include clear constraints and requirements
- Document relationships between parameters

## Future Extensions

### Adding New Collections
1. Create directory under `data/`
2. Add JSON files
3. Update `load_all_data.py` if needed

### Adding New Normalizers
1. Add class to `normalizers.py`
2. Update `normalize_module_data()` function
3. No database changes needed

## Common Operations

### Updating the Database
```bash
# Update everything
python load_all_data.py

# Or update specific collection
python load_data.py
```

### Generating Programs
```python
generator = ProgramGenerator()
program = generator.generate_program(your_requirements)
print(program["program"])
```

### Querying Specific Modules
```python
module = db.get_collection("loading_modules").get(
    ids=["cluster_90pct_1rm_12min"]
)
```

## Troubleshooting

### Data Not Showing Up
- Check JSON format
- Verify file locations
- Run load script again

### Query Not Finding Expected Results
- Check normalized values
- Try broader search terms
- Verify collection names

## Next Steps
1. Run the setup scripts
2. Load your existing data
3. Try generating a program
4. Experiment with queries
5. Add more data as needed

Need help? Check the code comments or create an issue in the repository.
