import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
from openai import OpenAI
import time

class LoadingModuleGenerator:
    def __init__(self):
        self.base_path = Path(r"C:\Users\Rob\Documents\ThreeStormFitness\GitGains\gitgains")
        self.loading_modules_path = self.base_path / "data" / "loading_modules"
        self.prompts_path = self.base_path / "prompts"
        
        # Read the prompts
        self.rewrite_prompt = (self.prompts_path / "rewrite_source_material.md").read_text(encoding='utf-8')
        self.json_prompt = (self.prompts_path / "create_JSON_from_source.md").read_text(encoding='utf-8')
        self.md_prompt = (self.prompts_path / "create_MD_from_sourceandJSON.md").read_text(encoding='utf-8')
        
        # Initialize OpenAI client
        self.client = None

    def select_source_folder(self):
        """Open a dialog to select the folder containing source files"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        folder_path = filedialog.askdirectory(title="Select folder containing source files")
        return folder_path if folder_path else None

    def process_source_file(self, source_file):
        """Process a single source file through the pipeline"""
        print(f"\nProcessing: {source_file}")
        
        # Read source content
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()

        # Step 1: Rewrite source material
        rewrite_response = self.get_openai_response(
            f"{self.rewrite_prompt}\n\nSource Content:\n{source_content}"
        )
        
        print("\nRewritten content generated. Please review:")
        print("----------------------------------------")
        print(rewrite_response)
        print("----------------------------------------")
        
        if not messagebox.askyesno("Review Rewrite", "Is the rewritten content acceptable?"):
            print("Rewrite rejected. Skipping file.")
            return
        
        # Step 2: Generate JSON for each module
        json_response = self.get_openai_response(
            f"{self.json_prompt}\n\nSource Content:\n{rewrite_response}"
        )
        
        try:
            json_data = json.loads(json_response)
            print("\nJSON generated. Please review:")
            print(json.dumps(json_data, indent=2))
            
            if not messagebox.askyesno("Review JSON", "Is the JSON content acceptable?"):
                print("JSON rejected. Skipping file.")
                return
            
            # Get module name from JSON for file naming
            module_id = json_data.get('id', 'unnamed_module')
            
            # Save the rewritten content as source MD
            source_md_path = self.loading_modules_path / f"{module_id}-source.md"
            with open(source_md_path, 'w', encoding='utf-8') as f:
                f.write(rewrite_response)
            
            # Save the JSON
            json_path = self.loading_modules_path / f"{module_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, sort_keys=False)
            
            # Step 3: Generate final MD
            md_response = self.get_openai_response(
                f"{self.md_prompt}\n\nJSON Data:\n{json_response}\n\nSource Material:\n{rewrite_response}"
            )
            
            # Save the MD
            md_path = self.loading_modules_path / f"{module_id}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_response)
            
            print(f"\nFiles generated successfully:")
            print(f"Source MD: {source_md_path}")
            print(f"JSON: {json_path}")
            print(f"Final MD: {md_path}")
            
        except json.JSONDecodeError:
            print("Error: Invalid JSON generated. Skipping file.")
            return
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return

    def get_openai_response(self, prompt):
        """Get response from OpenAI API using the latest API version"""
        try:
            completion = self.client.chat.completions.create(
                model="o1",  # Using the latest and most capable o1 model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=20000  # Increased token limit - o1 supports up to 128k tokens
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            raise

    def process_multiple_modules(self, rewrite_response):
        """Handle multiple modules in a single source"""
        if messagebox.askyesno("Multiple Modules", 
                             "Does this content contain multiple loading modules that should be processed separately?"):
            modules = []
            while True:
                module_text = self.get_openai_response(
                    f"Please extract the next distinct loading module from this content, or respond with 'NO_MORE_MODULES' if none remain:\n\n{rewrite_response}"
                )
                
                if module_text.strip() == "NO_MORE_MODULES":
                    break
                    
                modules.append(module_text)
                if not messagebox.askyesno("Continue", "Process another module from this content?"):
                    break
            
            return modules
        return [rewrite_response]

    def run(self):
        """Main execution flow"""
        # Ensure OpenAI API key is set
        if 'OPENAI_API_KEY' not in os.environ:
            api_key = simpledialog.askstring("OpenAI API Key", 
                                           "Please enter your OpenAI API key:",
                                           show='*')
            if not api_key:
                print("No API key provided. Exiting.")
                return
            os.environ['OPENAI_API_KEY'] = api_key
        
        # Initialize OpenAI client
        self.client = OpenAI()
        
        # Select source folder
        source_folder = self.select_source_folder()
        if not source_folder:
            print("No folder selected. Exiting.")
            return
        
        # Process each file in the folder
        for file in Path(source_folder).glob('*.*'):
            if file.is_file():
                self.process_source_file(file)
                time.sleep(1)  # Prevent rate limiting

if __name__ == "__main__":
    generator = LoadingModuleGenerator()
    generator.run()
