from typing import Union, Optional
import re

class TimeNormalizer:
    """Normalizes time values to minutes while preserving original format"""
    
    @staticmethod
    def to_minutes(time_value: Union[str, int, float, None]) -> Optional[float]:
        """Convert any time format to minutes"""
        if time_value is None or time_value == "N/A" or time_value == "varies" or time_value == "null":
            return None
            
        if isinstance(time_value, (int, float)):
            return float(time_value)
            
        # Convert string to lowercase for easier matching
        time_str = str(time_value).lower().strip()
        
        # Handle special cases
        if time_str in ["varies", "variable", "n/a", "null", ""]:
            return None
            
        # Extract numbers and units using regex
        match = re.search(r'(\d+(?:\.\d+)?)\s*(min|mins|minutes|sec|secs|seconds|s|m)?', time_str)
        if not match:
            return None
            
        value = float(match.group(1))
        unit = match.group(2) if match.group(2) else "min"  # Default to minutes if no unit
        
        # Convert to minutes
        if unit in ["sec", "secs", "seconds", "s"]:
            return value / 60
        return value

class LoadNormalizer:
    """Normalizes load/intensity values"""
    
    @staticmethod
    def to_percentage(load_value: Union[str, int, float, None]) -> Optional[float]:
        """Convert various load formats to percentage"""
        if load_value is None or load_value == "N/A" or load_value == "varies":
            return None
            
        if isinstance(load_value, (int, float)):
            return float(load_value)
            
        load_str = str(load_value).lower().strip()
        
        # Handle percentage
        if "%" in load_str:
            return float(load_str.replace("%", ""))
            
        # Handle RPE
        rpe_match = re.search(r'rpe\s*(\d+(?:\.\d+)?)', load_str)
        if rpe_match:
            rpe = float(rpe_match.group(1))
            # Convert RPE to approximate percentage (simplified conversion)
            return (rpe - 1) * 10
            
        # Handle RIR
        rir_match = re.search(r'rir\s*(\d+(?:\.\d+)?)', load_str)
        if rir_match:
            rir = float(rir_match.group(1))
            # Convert RIR to approximate percentage (simplified conversion)
            return 100 - (rir * 10)
            
        return None

def normalize_module_data(module_data: dict) -> dict:
    """Normalize a module's data while preserving original values"""
    normalized = module_data.copy()
    
    # Add normalized fields with _normalized suffix
    if 'avg_time_session' in module_data:
        normalized['avg_time_session_normalized'] = TimeNormalizer.to_minutes(module_data['avg_time_session'])
        
    if 'intensity_range' in module_data:
        normalized['intensity_range_normalized'] = LoadNormalizer.to_percentage(module_data['intensity_range'])
    
    return normalized
