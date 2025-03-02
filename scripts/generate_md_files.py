import json
import os
from openai import OpenAI
from pathlib import Path

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define paths
CURRENT_DIR = Path(__file__).parent.parent
JSON_FILE = CURRENT_DIR / "data" / "combined" / "from_o3_deepr_3_2_25.json"
PROMPT_FILE = CURRENT_DIR / "prompts" / "create_MD_from_sourceandJSON.md"
OUTPUT_DIR = CURRENT_DIR / "data" / "loading_modules"

def read_prompt():
    """Read the prompt template from the file."""
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def process_json_object(json_obj, prompt_template):
    """Process a single JSON object using GPT-4o."""
    try:
        # Prepare the messages for the API call
        messages = [
            {"role": "system", "content": "You are a technical writer specializing in creating markdown documentation for fitness training modules."},
            {"role": "user", "content": f"Here is the prompt template for creating the markdown:\n\n{prompt_template}\n\nAnd here is the JSON data to use:\n\n{json.dumps(json_obj, indent=2)}"}
        ]
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        # Extract the markdown content
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error processing JSON object: {e}")
        return None

def main():
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read the prompt template
    prompt_template = read_prompt()
    
    # Read and process the JSON file
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    # Process each JSON object in the loading_modules array
    for json_obj in json_data['loading_modules']:
        try:
            # Get the ID from the JSON object
            module_id = json_obj.get('id')
            if not module_id:
                print(f"Warning: JSON object missing ID field, skipping: {json_obj}")
                continue
                
            # Generate the markdown
            markdown_content = process_json_object(json_obj, prompt_template)
            if not markdown_content:
                continue
                
            # Write to file
            output_file = OUTPUT_DIR / f"{module_id}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            print(f"Successfully processed module: {module_id}")
            
        except Exception as e:
            print(f"Error processing module: {e}")
            continue

if __name__ == "__main__":
    main()
