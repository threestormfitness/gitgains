import os
import json
import time
import logging
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox, simpledialog

class TimeUpdater:
    def __init__(self):
        self.base_path = Path(r"C:\Users\Rob\Documents\ThreeStormFitness\GitGains\GitGains")
        self.loading_modules_path = self.base_path / "data" / "loading_modules"
        self.prompts_path = self.base_path / "prompts"
        self.log_path = self.base_path / "scripts" / "logs" / "update_time_in_batches.log"
        
        # Ensure log directory exists
        self.log_path.parent.mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Read the timing rules from create_JSON_from_source.md
        self.timing_rules = (self.prompts_path / "create_JSON_from_source.md").read_text(encoding='utf-8')
        
        # Extract just the "Expanded Time Calculation Rules" section
        time_rules_match = re.search(r'### Expanded Time Calculation Rules(.*?)---', self.timing_rules, re.DOTALL)
        if time_rules_match:
            self.time_rules = time_rules_match.group(1).strip()
        else:
            self.time_rules = "Time calculation rules not found."
        
        # Initialize OpenAI client
        self.client = None
        
    def setup_openai(self):
        """Set up the OpenAI client with API key"""
        if 'OPENAI_API_KEY' not in os.environ:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            api_key = simpledialog.askstring("OpenAI API Key", 
                                           "Please enter your OpenAI API key:",
                                           show='*')
            if not api_key:
                print("No API key provided. Exiting.")
                return False
            os.environ['OPENAI_API_KEY'] = api_key
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        return True
    
    def get_last_processed_file(self):
        """Read the log file to find the last processed file"""
        if not self.log_path.exists():
            return None
        
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return None
            
        # Process lines in reverse to find the last successfully processed file
        for line in reversed(lines):
            if "Updated time info" in line or "Renamed from" in line:
                # Extract filename from log entry
                match = re.search(r'- (.*?) -', line)
                if match:
                    return match.group(1)
        
        return None
    
    def get_json_files(self):
        """Get all JSON files in the loading_modules directory"""
        return sorted([f for f in self.loading_modules_path.glob('*.json') 
                      if f.name != 'thib_642wave_approx12m.json'])  # Exclude the specified file
    
    def determine_module_type(self, json_data):
        """Determine if a module is standard or unorthodox based on its properties"""
        # Check for indicators of unorthodox modules
        if (json_data.get('pyramid', 'no') == 'yes' or 
            json_data.get('wave_sets', 'no') == 'yes' or 
            json_data.get('ladder_sets', 'n/a') != 'n/a' or 
            json_data.get('cluster', 'no') == 'yes' or 
            json_data.get('density_sets', 'no') == 'yes' or
            json_data.get('emom', 'no') == 'yes' or
            json_data.get('timed', 'no') == 'yes' or
            'complex' in json_data.get('superset_type', 'N/A').lower() or
            'circuit' in json_data.get('superset_type', 'N/A').lower()):
            return "unorthodox"
        return "standard"
    
    def get_time_estimate(self, json_data, json_path):
        """Get time estimate from o1-mini model"""
        module_type = self.determine_module_type(json_data)
        
        # Create a prompt for the o1-mini model
        prompt = f"""
You are an expert in strength training and exercise science. Your task is to calculate the time required for a strength training loading module.

Here are the time calculation rules to follow:
{self.time_rules}

Here is the loading module data:
{json.dumps(json_data, indent=2)}

This module appears to be a {module_type} type module.

Please analyze the module and provide:
1. The average time per session in minutes (a single number or small range)
2. A brief explanation of how you calculated this time (time_per_session_breakdown)
3. If this is an unorthodox module with multiple possible scenarios, please provide a detailed time_analysis object with min/max/average scenarios

Return your answer in JSON format with these fields:
{{
  "avg_time_session": number or small range,
  "time_per_session_breakdown": "explanation string",
  "time_analysis": {{ optional detailed breakdown if multiple scenarios exist }}
}}

IMPORTANT: Your entire response must be valid JSON. Do not include any text before or after the JSON.
"""

        try:
            # Call the o1-mini model
            completion = self.client.chat.completions.create(
                model="o1-mini",  # Using o1-mini as specified
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=2000  # Using max_completion_tokens instead of max_tokens
            )
            
            response_text = completion.choices[0].message.content.strip()
            print(f"Raw response from o1-mini for {json_path.name}:")
            print(response_text)
            
            # Try to parse the JSON response
            try:
                time_data = json.loads(response_text)
                return time_data
            except json.JSONDecodeError:
                # If the response isn't valid JSON, try to extract the JSON part
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    try:
                        time_data = json.loads(json_match.group(1))
                        return time_data
                    except:
                        pass
                
                # Try to extract just the JSON object from the text
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    try:
                        time_data = json.loads(json_match.group(1))
                        return time_data
                    except:
                        pass
                
                # If all parsing attempts fail, try to extract key information manually
                avg_time_match = re.search(r'"avg_time_session":\s*(\d+)', response_text)
                breakdown_match = re.search(r'"time_per_session_breakdown":\s*"([^"]+)"', response_text)
                
                if avg_time_match:
                    avg_time = int(avg_time_match.group(1))
                    breakdown = breakdown_match.group(1) if breakdown_match else "Extracted from partial response"
                    
                    return {
                        "avg_time_session": avg_time,
                        "time_per_session_breakdown": breakdown
                    }
                
                # Log the error and return a default response
                logging.error(f"Failed to parse JSON response for {json_path.name}")
                print(f"Error: Failed to parse JSON response for {json_path.name}")
                return {
                    "avg_time_session": json_data.get("avg_time_session", "varies"),
                    "time_per_session_breakdown": "Failed to calculate new time estimate"
                }
                
        except Exception as e:
            logging.error(f"Error calling OpenAI API for {json_path.name}: {str(e)}")
            print(f"Error calling OpenAI API: {str(e)}")
            return {
                "avg_time_session": json_data.get("avg_time_session", "varies"),
                "time_per_session_breakdown": "Failed to calculate new time estimate"
            }
    
    def generate_new_id(self, json_data, old_id):
        """Generate a new ID with updated time reference"""
        # Extract components from the old ID
        # Remove time references like _15min, _approx10m, etc.
        base_id = re.sub(r'_\d+min|_approx\d+m?', '', old_id)
        
        # Get the new time estimate
        avg_time = json_data.get('avg_time_session', '')
        
        # If avg_time is a number, format it as minutes
        if isinstance(avg_time, (int, float)):
            # Round to nearest minute
            new_id = f"{base_id}_{int(round(avg_time))}min"
        # If avg_time is a string that might contain a range or "varies"
        elif isinstance(avg_time, str):
            if avg_time.lower() == 'varies':
                new_id = f"{base_id}_varies"
            elif '-' in avg_time:  # It's a range like "10-15"
                # Extract the average of the range
                try:
                    parts = avg_time.split('-')
                    min_val = int(parts[0].strip())
                    max_val = int(parts[1].strip())
                    avg_val = (min_val + max_val) // 2
                    new_id = f"{base_id}_approx{avg_val}m"
                except:
                    # If parsing fails, just use the base ID
                    new_id = base_id
            else:
                # Try to convert to int
                try:
                    time_val = int(avg_time)
                    new_id = f"{base_id}_{time_val}min"
                except:
                    # If conversion fails, just use the base ID
                    new_id = base_id
        else:
            # If avg_time is not a recognized format, keep the base ID
            new_id = base_id
            
        return new_id
    
    def process_file(self, json_path):
        """Process a single JSON file"""
        try:
            # Read the JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            old_id = json_data.get('id', '')
            
            # Get time estimate from o1-mini
            time_data = self.get_time_estimate(json_data, json_path)
            
            # Update the JSON with new time data
            json_data['avg_time_session'] = time_data.get('avg_time_session', json_data.get('avg_time_session', 'varies'))
            json_data['time_per_session_breakdown'] = time_data.get('time_per_session_breakdown', json_data.get('time_per_session_breakdown', ''))
            
            # Add time_analysis if it exists in the response
            if 'time_analysis' in time_data:
                json_data['time_analysis'] = time_data['time_analysis']
            
            # Generate new ID
            new_id = self.generate_new_id(json_data, old_id)
            json_data['id'] = new_id
            
            # Save updated JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"- {json_path.name} - Updated time info")
            print(f"Updated time info for {json_path.name}")
            
            # Rename files if ID changed
            if new_id != old_id:
                # Rename JSON file
                new_json_path = json_path.parent / f"{new_id}.json"
                json_path.rename(new_json_path)
                
                # Check if corresponding MD file exists and rename it
                md_path = json_path.parent / f"{old_id}.md"
                if md_path.exists():
                    new_md_path = json_path.parent / f"{new_id}.md"
                    md_path.rename(new_md_path)
                    logging.info(f"- {old_id} - Renamed to {new_id}")
                    print(f"Renamed {old_id} to {new_id}")
                else:
                    logging.info(f"- {old_id} - Renamed JSON only (no MD file found)")
                    print(f"Renamed JSON only for {old_id} (no MD file found)")
                
                return new_json_path
            
            return json_path
            
        except Exception as e:
            logging.error(f"- {json_path.name} - Error processing file: {str(e)}")
            print(f"Error processing {json_path.name}: {str(e)}")
            return json_path
    
    def process_files_in_batches(self, files, batch_size=5, start_index=0):
        """Process files in batches of specified size"""
        total_files = len(files)
        
        for i in range(start_index, total_files, batch_size):
            batch = files[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} of {(total_files + batch_size - 1)//batch_size}")
            
            # Process each file in the batch
            for file_path in batch:
                self.process_file(file_path)
            
            # After each batch, ask if we should continue
            if i + batch_size < total_files:
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                continue_processing = messagebox.askyesno(
                    "Continue Processing?",
                    f"Processed {i + len(batch)} of {total_files} files. Continue to the next batch?"
                )
                
                if not continue_processing:
                    logging.info(f"Processing stopped after {i + len(batch)} files")
                    print(f"Processing stopped after {i + len(batch)} files")
                    break
    
    def run(self):
        """Main execution flow"""
        # Set up OpenAI client
        if not self.setup_openai():
            return
        
        # Get all JSON files
        all_files = self.get_json_files()
        if not all_files:
            print("No JSON files found in the loading_modules directory")
            return
            
        print(f"Found {len(all_files)} JSON files to process")
        
        # Ask if we should resume from last processed file
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        resume = messagebox.askyesno("Resume Processing?", "Resume from last updated file (Y/N)?")
        
        start_index = 0
        if resume:
            last_file = self.get_last_processed_file()
            if last_file:
                # Find the index of the last processed file
                for i, file_path in enumerate(all_files):
                    if file_path.name == last_file or file_path.stem == last_file:
                        start_index = i + 1
                        break
                
                print(f"Resuming from file #{start_index + 1} (after {last_file})")
                logging.info(f"Resuming processing from index {start_index}")
            else:
                print("No previous processing found, starting from the beginning")
        
        # Process files in batches
        self.process_files_in_batches(all_files, batch_size=5, start_index=start_index)
        
        print("\nProcessing complete!")

if __name__ == "__main__":
    updater = TimeUpdater()
    updater.run()
