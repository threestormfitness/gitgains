import json
import os

# Define paths
input_file = r"C:\Users\Rob\Documents\ThreeStormFitness\GitGains\GitGains\data\combined\from_o3_deepr_3_2_25.json"
output_dir = r"C:\Users\Rob\Documents\ThreeStormFitness\GitGains\gitgains\data\loading_modules"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Read the input JSON file
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract the loading modules array
loading_modules = data.get('loading_modules', [])

# Process each module
for module in loading_modules:
    if 'id' in module:
        # Create filename using the id
        output_file = os.path.join(output_dir, f"{module['id']}.json")
        
        # Write individual JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(module, f, indent=2, ensure_ascii=False)

print(f"Successfully split {len(loading_modules)} JSON objects into individual files in {output_dir}")
