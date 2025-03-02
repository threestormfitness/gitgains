import json
import os
from pathlib import Path

# Define paths
base_dir = Path(__file__).parent.parent
input_dir = base_dir / 'data' / 'loading_modules'
output_dir = base_dir / 'data' / 'combined'
output_file = output_dir / 'all_loading_modules.json'

def combine_json_files():
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Initialize empty list to store all modules
    all_modules = []
    
    # Iterate through all JSON files in the input directory
    for file_path in input_dir.glob('*.json'):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    module_data = json.load(f)
                    all_modules.append(module_data)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
            except Exception as e:
                print(f"Unexpected error with {file_path}: {e}")
    
    # Sort modules by ID for consistency
    all_modules.sort(key=lambda x: x.get('id', ''))
    
    # Write combined data to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'loading_modules': all_modules,
            'total_count': len(all_modules)
        }, f, indent=2)
    
    print(f"Successfully combined {len(all_modules)} loading modules into {output_file}")

if __name__ == '__main__':
    combine_json_files()
