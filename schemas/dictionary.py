"""
Pydantic schemas for dictionary endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DictionaryCreate(BaseModel):
    """Schema for creating a dictionary."""
    name: str = Field(..., min_length=1, max_length=100, description="Dictionary name")
    description: Optional[str] = Field(None, max_length=500, description="Dictionary description")

class DictionaryUpdate(BaseModel):
    """Schema for updating a dictionary."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Dictionary name")
    description: Optional[str] = Field(None, max_length=500, description="Dictionary description")

class DictionaryResponse(BaseModel):
    """Schema for dictionary response."""
    id: str
    name: str
    description: str
    word_count: int
    created_at: str
    updated_at: str

class WordCreate(BaseModel):
    """Schema for creating a word."""
    word: str = Field(..., min_length=1, max_length=100, description="Word")
    definition: str = Field(..., min_length=1, max_length=1000, description="Definition")
    pronunciation: Optional[str] = Field(None, max_length=100, description="Pronunciation")
    examples: Optional[List[str]] = Field(default_factory=list, description="Examples")
    categories: Optional[List[str]] = Field(default_factory=list, description="Categories")
    notes: Optional[str] = Field(None, max_length=500, description="Notes")

class WordUpdate(BaseModel):
    """Schema for updating a word."""
    word: Optional[str] = Field(None, min_length=1, max_length=100, description="Word")
    definition: Optional[str] = Field(None, min_length=1, max_length=1000, description="Definition")
    pronunciation: Optional[str] = Field(None, max_length=100, description="Pronunciation")
    examples: Optional[List[str]] = Field(None, description="Examples")
    categories: Optional[List[str]] = Field(None, description="Categories")
    notes: Optional[str] = Field(None, max_length=500, description="Notes")

class WordResponse(BaseModel):
    """Schema for word response."""
    id: str
    word: str
    definition: str
    pronunciation: str
    examples: List[str]
    categories: List[str]
    notes: str
    created_at: str
    updated_at: str

class WordSearch(BaseModel):
    """Schema for word search."""
    query: str = Field(..., min_length=1, description="Search query")
    search_type: str = Field(default="word", description="Search type: word, definition, or both")

class ImportData(BaseModel):
    """Schema for importing data."""
    data: str = Field(..., description="JSON or CSV data to import")
    format: str = Field(..., description="Data format: json or csv")

class ExportFormat(BaseModel):
    """Schema for export format selection."""
    format: str = Field(..., description="Export format: json or csv")

class BulkWordCreate(BaseModel):
    """Schema for bulk word creation."""
    words: List[WordCreate] = Field(..., description="List of words to create")

class SearchResponse(BaseModel):
    """Schema for search response."""
    words: List[WordResponse]
    total_count: int
    query: str
    search_type: str
