import os
from pathlib import Path

# Define paths
base_dir = Path(__file__).parent.parent
input_dir = base_dir / 'data' / 'loading_modules'
output_dir = base_dir / 'data' / 'combined'
output_file = output_dir / 'all_loading_modules.md'

def combine_md_files():
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Get all MD files and sort them
    md_files = sorted([f for f in input_dir.glob('*.md') if f.is_file()])
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write('# Loading Modules Documentation\n\n')
        outfile.write('This document contains all loading module documentation combined into a single file.\n\n')
        outfile.write('---\n\n')
        
        # Process each MD file
        for i, file_path in enumerate(md_files, 1):
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    
                # Add decorative separator and file number
                outfile.write(f'# Module {i}: {file_path.stem}\n')
                outfile.write('=' * 80 + '\n\n')
                
                # Write the content
                outfile.write(content)
                
                # Add separator between modules
                outfile.write('\n\n' + '-' * 80 + '\n\n')
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
    print(f"Successfully combined {len(md_files)} markdown files into {output_file}")

if __name__ == '__main__':
    combine_md_files()
