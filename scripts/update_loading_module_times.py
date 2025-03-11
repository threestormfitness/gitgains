import os
import json
import glob
from openai import OpenAI
from typing import Dict, Tuple, List, Optional

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_unorthodox_structure(module_info: Dict) -> bool:
    """
    Check if the module has an unorthodox structure that doesn't follow standard timing rules
    """
    # Keywords that suggest unorthodox timing
    unorthodox_indicators = [
        'pyramid', 'complex', 'EDT', 'density', 'EMOM', 'circuit',
        'timed', 'min', 'minute', 'interval', 'tabata'
    ]
    
    # Check various fields for these indicators
    fields_to_check = [
        module_info.get('time_breakdown', '').lower(),
        module_info.get('overview', '').lower(),
        module_info.get('name', '').lower(),
        module_info.get('id', '').lower()
    ]
    
    # Also check specific module attributes
    if (module_info.get('timed') == 'yes' or
        module_info.get('emom') == 'yes' or
        module_info.get('density_sets') == 'yes' or
        module_info.get('ladder_sets') == 'pyramid'):
        return True
        
    # Check for keywords in any field
    for field in fields_to_check:
        for indicator in unorthodox_indicators:
            if indicator in field:
                return True
                
    return False

def calculate_standard_timing(module_info: Dict) -> Dict:
    """
    Calculate timing using standard rules from the prompt
    """
    prompt = f"""
    Calculate the precise timing for this workout module using these STRICT rules:
    1. Standard sets: 30-45 seconds per set
    2. Explosive sets (<5 reps): 15-25 seconds per set
    3. Heavy set rest (≤5 reps): 3-5 minutes (180-300 seconds)
    4. Regular rest (≥6 reps): 90-120 seconds
    5. "As little as possible" rest: 15 seconds
    6. Do NOT include warmups
    7. Do NOT include assistance/accessory work
    8. Round final times to nearest minute
    
    Module Information:
    - Sets: {module_info.get('total_sets')}
    - Reps: {module_info.get('reps')}
    - Intensity: {module_info.get('intensity_range')}
    
    Additional Context:
    {module_info.get('overview')}
    
    Return a JSON object with:
    1. Set Calculations:
    - set_type: "standard" or "explosive"
    - sets_per_session: number of working sets
    - time_per_set: range in seconds
    - total_set_time_min: minimum total set time in seconds
    - total_set_time_max: maximum total set time in seconds
    
    2. Rest Calculations:
    - rest_type: "heavy" or "regular" or "minimal"
    - rest_between_sets: range in seconds
    - total_rest_time_min: minimum total rest time in seconds
    - total_rest_time_max: maximum total rest time in seconds
    
    3. Total Times (in minutes, rounded to nearest minute):
    - min_time: minimum total time
    - max_time: maximum total time
    - avg_time: average of min and max
    
    4. Analysis:
    - calculation_method: detailed explanation of the calculation
    - key_factors: array of main factors affecting timing
    - confidence_level: high/medium/low
    
    Return only the JSON object, nothing else.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a precise workout time calculator that follows strict timing rules."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response content
        content = response.choices[0].message.content.strip()
        time_info = json.loads(content)
        
        # Ensure required fields exist
        required_fields = ['min_time', 'max_time', 'avg_time']
        for field in required_fields:
            if field not in time_info:
                raise KeyError(f"Missing required field: {field}")
        
        return time_info
        
    except Exception as e:
        print(f"Error calculating standard timing: {str(e)}")
        print(f"Module info: {module_info}")
        raise

def analyze_unorthodox_timing(module_info: Dict) -> Dict:
    """
    Analyze timing for unorthodox structures using their specific timing rules
    """
    prompt = f"""
    Analyze this unorthodox workout module's timing. Use ONLY the explicitly stated timing information.
    DO NOT apply standard set/rest calculations.
    
    Module Information:
    Time Breakdown: {module_info.get('time_breakdown')}
    Overview: {module_info.get('overview')}
    Example: {module_info.get('example')}
    Notes: {module_info.get('notes')}
    
    Additional Context:
    - Total Sets: {module_info.get('total_sets')}
    - Reps: {module_info.get('reps')}
    - Timed: {module_info.get('timed')}
    - EMOM: {module_info.get('emom')}
    - Density Sets: {module_info.get('density_sets')}
    - Ladder Sets: {module_info.get('ladder_sets')}
    
    Return a JSON object with:
    1. Timing Analysis:
    - min_time: minimum total time in minutes
    - max_time: maximum total time in minutes
    - avg_time: average time in minutes
    
    2. Variations:
    - timing_scenarios: array of timing scenarios, each with:
      * scenario_name: description
      * min_time: minimum minutes
      * max_time: maximum minutes
      * conditions: what leads to this timing
    
    3. Analysis:
    - calculation_method: how times were calculated
    - key_factors: array of factors affecting timing
    - confidence_level: high/medium/low
    - timing_notes: important timing notes
    
    Return only the JSON object, nothing else.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a precise workout time analyzer specializing in unorthodox training methods."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response content
        content = response.choices[0].message.content.strip()
        time_info = json.loads(content)
        
        # Ensure required fields exist
        required_fields = ['min_time', 'max_time', 'avg_time']
        for field in required_fields:
            if field not in time_info:
                raise KeyError(f"Missing required field: {field}")
        
        return time_info
        
    except Exception as e:
        print(f"Error analyzing unorthodox timing: {str(e)}")
        print(f"Module info: {module_info}")
        raise

def format_time_analysis(time_info: Dict, is_unorthodox: bool) -> str:
    """Format time information into a detailed readable string"""
    try:
        # Basic time range
        base_range = f"{time_info['min_time']}-{time_info['max_time']} minutes (avg: {time_info['avg_time']} min)"
        
        # For standard timing, add set/rest breakdown
        if not is_unorthodox and 'set_type' in time_info:
            details = [
                f"Set type: {time_info['set_type']} ({time_info['time_per_set']}s per set)",
                f"Rest: {time_info['rest_type']} ({time_info['rest_between_sets']}s between sets)"
            ]
            base_range += f"\nBreakdown: {'; '.join(details)}"
        
        # Add scenarios for unorthodox timing
        if is_unorthodox and 'timing_scenarios' in time_info:
            scenarios = [
                f"\n- {s['scenario_name']}: {s['min_time']}-{s['max_time']} min ({s['conditions']})"
                for s in time_info['timing_scenarios']
            ]
            if scenarios:
                base_range += "\nTiming Scenarios:" + ''.join(scenarios)
        
        # Add analysis
        analysis = []
        if 'calculation_method' in time_info:
            analysis.append(f"Calculation: {time_info['calculation_method']}")
        if 'key_factors' in time_info:
            analysis.append(f"Key factors: {', '.join(time_info['key_factors'])}")
        if 'confidence_level' in time_info:
            analysis.append(f"Confidence: {time_info['confidence_level']}")
        
        if analysis:
            base_range += "\n" + "\n".join(analysis)
        
        return base_range
        
    except Exception as e:
        print(f"Error formatting time analysis: {str(e)}")
        print(f"Time info: {time_info}")
        raise

def update_loading_module_files(base_dir: str):
    """Update all loading module files with detailed time information"""
    loading_modules_dir = os.path.join(base_dir, 'data', 'loading_modules')
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(loading_modules_dir, '*.json'))
    
    for json_file in json_files:
        try:
            md_file = json_file.replace('.json', '.md')
            
            # Skip if MD file doesn't exist
            if not os.path.exists(md_file):
                continue
                
            print(f"\nProcessing {os.path.basename(json_file)}...")
            
            # Read both files
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
                
            # Prepare module info
            module_info = {
                'time_breakdown': json_data.get('time_per_session_breakdown', ''),
                'overview': json_data.get('overview_and_execution', ''),
                'example': json_data.get('example_application', ''),
                'notes': json_data.get('important_notes', ''),
                'total_sets': json_data.get('total_sets', ''),
                'reps': json_data.get('reps', ''),
                'intensity_range': json_data.get('intensity_range', ''),
                'name': json_data.get('name', ''),
                'id': json_data.get('id', ''),
                'timed': json_data.get('timed', 'no'),
                'emom': json_data.get('emom', 'no'),
                'density_sets': json_data.get('density_sets', 'no'),
                'ladder_sets': json_data.get('ladder_sets', 'n/a')
            }
            
            # Check if this is an unorthodox structure
            is_unorthodox = is_unorthodox_structure(module_info)
            print(f"Module type: {'Unorthodox' if is_unorthodox else 'Standard'} timing")
            
            # Get timing analysis
            if is_unorthodox:
                time_info = analyze_unorthodox_timing(module_info)
            else:
                time_info = calculate_standard_timing(module_info)
            
            # Format the time range
            time_range = format_time_analysis(time_info, is_unorthodox)
            
            # Update JSON file
            json_data['avg_time_session'] = time_info['avg_time']
            json_data['time_analysis'] = {
                'is_unorthodox_timing': is_unorthodox,
                'time_range': f"{time_info['min_time']}-{time_info['max_time']} min",
                'average_time': time_info['avg_time'],
                'calculation_method': time_info.get('calculation_method', ''),
                'key_factors': time_info.get('key_factors', []),
                'confidence_level': time_info.get('confidence_level', '')
            }
            
            # Add specific fields based on timing type
            if is_unorthodox:
                json_data['time_analysis'].update({
                    'timing_scenarios': time_info.get('timing_scenarios', []),
                    'timing_notes': time_info.get('timing_notes', '')
                })
            else:
                json_data['time_analysis'].update({
                    'set_calculations': {
                        'set_type': time_info.get('set_type', ''),
                        'time_per_set': time_info.get('time_per_set', ''),
                        'total_set_time_range': f"{time_info.get('total_set_time_min', 0)}-{time_info.get('total_set_time_max', 0)}s"
                    },
                    'rest_calculations': {
                        'rest_type': time_info.get('rest_type', ''),
                        'rest_between_sets': time_info.get('rest_between_sets', ''),
                        'total_rest_time_range': f"{time_info.get('total_rest_time_min', 0)}-{time_info.get('total_rest_time_max', 0)}s"
                    }
                })
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            
            # Update MD file
            old_time = f"**Average Time per Session**   | {json_data.get('avg_time_session', '')} minutes"
            new_time = f"**Average Time per Session**   | {time_range}"
            
            if old_time in md_content:
                md_content = md_content.replace(old_time, new_time)
            else:
                # Try to find the line with "Average Time per Session" and update it
                lines = md_content.split('\n')
                for i, line in enumerate(lines):
                    if "**Average Time per Session**" in line:
                        lines[i] = new_time
                        break
                md_content = '\n'.join(lines)
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            print(f"Successfully updated {os.path.basename(json_file)} and {os.path.basename(md_file)}")
            
        except Exception as e:
            print(f"\nError processing {os.path.basename(json_file)}: {str(e)}")
            continue

if __name__ == "__main__":
    # Get the base directory (assuming script is in scripts/ directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    update_loading_module_files(base_dir)
