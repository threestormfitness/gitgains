from typing import Optional, List, Union
from pydantic import BaseModel, Field

class TimeRange(BaseModel):
    """Flexible time range representation"""
    min_time: int
    max_time: int
    explanation: Optional[str] = None

class LoadingModule(BaseModel):
    """Pydantic model for loading modules with flexible schema"""
    id: str
    name: str
    author_source: str
    cycle_duration: str
    total_sets: str
    reps: str
    intensity_unit: str
    intensity_range: str
    avg_time_session: Union[int, TimeRange, str]  # Can be number, range, or description
    overview_and_execution: str
    example_application: str
    important_notes: str
    volume_metrics: str
    markdown_content: Optional[str] = None  # Content from MD file
    source_content: Optional[str] = None    # Content from source MD
    
    # Allow additional fields
    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

class DatabaseConfig(BaseModel):
    """Configuration for the database"""
    persist_directory: str = Field(default="db")
    collection_name: str = Field(default="loading_modules")
    embedding_function: str = Field(default="all-MiniLM-L6-v2")
