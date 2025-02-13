import os
from typing import List, Dict, Any
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from models import DatabaseConfig
from db import GitGainsDB

# Load environment variables (for API key)
load_dotenv()

class ProgramGenerator:
    def __init__(self):
        self.db = GitGainsDB(DatabaseConfig())
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        
    def find_suitable_modules(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find loading modules that match specific criteria"""
        # Example: Find modules that fit within time constraints
        query = f"""
        Find modules that:
        - Take approximately {criteria.get('time_per_exercise', '10-15')} minutes
        - Focus on {criteria.get('training_type', 'strength')}
        - {'Include power development' if criteria.get('include_power') else ''}
        """
        
        results = self.db.query(query, n_results=10)
        return results
    
    def generate_program(self, requirements: str) -> Dict[str, Any]:
        """Generate a complete program based on requirements"""
        
        # First, get relevant loading modules from our database
        modules = self.find_suitable_modules({
            'time_per_exercise': '10-15',
            'include_power': True
        })
        
        # Create a context with our modules
        module_context = "\n".join([
            f"Module '{m['metadata']['name']}': {m['metadata']['overview_and_execution']}"
            for m in modules['metadatas']
        ])
        
        # Generate program using OpenAI
        messages = [
            {"role": "system", "content": f"""
            You are an expert strength coach with access to these loading modules:
            {module_context}
            
            Create a program that:
            1. Uses these loading modules appropriately
            2. Considers time constraints
            3. Follows proper exercise selection
            4. Includes proper progression
            """},
            {"role": "user", "content": requirements}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        
        program = response.choices[0].message.content
        
        return {
            "program": program,
            "used_modules": modules
        }

def main():
    generator = ProgramGenerator()
    
    # Example requirements
    requirements = """
    Create a resistance training program that:
    - 3 training sessions per week
    - Full body split (work push/pull/legs every session)
    - 1 hour per session (15 min for warmup/setup)
    - Commercial gym equipment available
    - Advanced 40-year-old lifter
    - Mix of strength, hypertrophy, and power
    - Include unilateral work
    - Focus on powerlifting movements
    """
    
    result = generator.generate_program(requirements)
    
    # Print the program
    print("\nGenerated Program:")
    print("=" * 80)
    print(result["program"])
    
    print("\nUsed Loading Modules:")
    print("=" * 80)
    for module in result["used_modules"]["metadatas"]:
        print(f"- {module['name']}: {module['overview_and_execution'][:100]}...")

if __name__ == "__main__":
    main()
