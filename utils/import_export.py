"""
Import/Export utilities for dictionary data.
"""

import json
import csv
import pandas as pd
from typing import List, Dict, Any, Tuple
from io import StringIO
from datetime import datetime
from utils.imports import ObjectId
from models.dictionary import Dictionary
from models.word import Word
import logging

class ImportExportManager:
    """Manager for import/export operations."""
    
    @staticmethod
    def export_dictionary_to_json(dictionary: Dictionary) -> str:
        """Export dictionary and all its words to JSON format."""
        try:
            # Get all words for the dictionary
            words = Word.get_by_dictionary(dictionary._id)
            
            # Prepare export data
            export_data = {
                "dictionary": {
                    "name": dictionary.name,
                    "description": dictionary.description,
                    "created_at": dictionary.created_at.isoformat(),
                    "word_count": len(words)
                },
                "words": []
            }
            
            # Add words data
            for word in words:
                word_data = {
                    "word": word.word,
                    "definition": word.definition,
                    "pronunciation": word.pronunciation,
                    "examples": word.examples,
                    "categories": word.categories,
                    "notes": word.notes,
                    "created_at": word.created_at.isoformat()
                }
                export_data["words"].append(word_data)
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        except Exception as e:
            logging.error(f"Error exporting to JSON: {e}")
            return ""
    
    @staticmethod
    def export_dictionary_to_csv(dictionary: Dictionary) -> str:
        """Export dictionary words to CSV format."""
        try:
            # Get all words for the dictionary
            words = Word.get_by_dictionary(dictionary._id)
            
            if not words:
                return "word,definition,pronunciation,examples,categories,notes\n"
            
            # Prepare CSV data
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "word", "definition", "pronunciation", 
                "examples", "categories", "notes"
            ])
            
            # Write word data
            for word in words:
                writer.writerow([
                    word.word,
                    word.definition,
                    word.pronunciation,
                    "; ".join(word.examples),
                    ", ".join(word.categories),
                    word.notes
                ])
            
            return output.getvalue()
        
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            return ""
    
    @staticmethod
    def import_from_json(json_data: str, dictionary_id: ObjectId) -> Tuple[int, int, List[str]]:
        """
        Import words from JSON data.
        Returns: (success_count, error_count, error_messages)
        """
        success_count = 0
        error_count = 0
        error_messages = []
        
        try:
            data = json.loads(json_data)
            
            # Validate JSON structure
            if "words" not in data:
                error_messages.append("Invalid JSON format: 'words' key not found")
                return 0, 1, error_messages
            
            words_data = data["words"]
            if not isinstance(words_data, list):
                error_messages.append("Invalid JSON format: 'words' should be a list")
                return 0, 1, error_messages
            
            # Process each word
            for i, word_data in enumerate(words_data):
                try:
                    # Validate required fields
                    if "word" not in word_data or "definition" not in word_data:
                        error_messages.append(f"Row {i+1}: Missing required fields (word, definition)")
                        error_count += 1
                        continue
                    
                    word_text = word_data["word"].strip()
                    definition = word_data["definition"].strip()
                    
                    if not word_text or not definition:
                        error_messages.append(f"Row {i+1}: Word and definition cannot be empty")
                        error_count += 1
                        continue
                    
                    # Check if word already exists
                    if Word.word_exists(word_text, dictionary_id):
                        error_messages.append(f"Row {i+1}: Word '{word_text}' already exists")
                        error_count += 1
                        continue
                    
                    # Create word object
                    word = Word(
                        word=word_text,
                        definition=definition,
                        dictionary_id=dictionary_id,
                        pronunciation=word_data.get("pronunciation", ""),
                        examples=word_data.get("examples", []),
                        categories=word_data.get("categories", []),
                        notes=word_data.get("notes", "")
                    )
                    
                    if word.save():
                        success_count += 1
                    else:
                        error_messages.append(f"Row {i+1}: Failed to save word '{word_text}'")
                        error_count += 1
                
                except Exception as e:
                    error_messages.append(f"Row {i+1}: {str(e)}")
                    error_count += 1
        
        except json.JSONDecodeError as e:
            error_messages.append(f"Invalid JSON format: {str(e)}")
            error_count += 1
        except Exception as e:
            error_messages.append(f"Import error: {str(e)}")
            error_count += 1
        
        return success_count, error_count, error_messages
    
    @staticmethod
    def import_from_csv(csv_data: str, dictionary_id: ObjectId) -> Tuple[int, int, List[str]]:
        """
        Import words from CSV data.
        Returns: (success_count, error_count, error_messages)
        """
        success_count = 0
        error_count = 0
        error_messages = []
        
        try:
            # Parse CSV data
            csv_file = StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            
            # Validate required columns
            required_columns = ["word", "definition"]
            if not all(col in reader.fieldnames for col in required_columns):
                error_messages.append(f"Missing required columns: {required_columns}")
                return 0, 1, error_messages
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is row 1)
                try:
                    word_text = row.get("word", "").strip()
                    definition = row.get("definition", "").strip()
                    
                    if not word_text or not definition:
                        error_messages.append(f"Row {row_num}: Word and definition cannot be empty")
                        error_count += 1
                        continue
                    
                    # Check if word already exists
                    if Word.word_exists(word_text, dictionary_id):
                        error_messages.append(f"Row {row_num}: Word '{word_text}' already exists")
                        error_count += 1
                        continue
                    
                    # Parse examples and categories
                    examples = []
                    if row.get("examples"):
                        examples = [ex.strip() for ex in row["examples"].split(";") if ex.strip()]
                    
                    categories = []
                    if row.get("categories"):
                        categories = [cat.strip() for cat in row["categories"].split(",") if cat.strip()]
                    
                    # Create word object
                    word = Word(
                        word=word_text,
                        definition=definition,
                        dictionary_id=dictionary_id,
                        pronunciation=row.get("pronunciation", "").strip(),
                        examples=examples,
                        categories=categories,
                        notes=row.get("notes", "").strip()
                    )
                    
                    if word.save():
                        success_count += 1
                    else:
                        error_messages.append(f"Row {row_num}: Failed to save word '{word_text}'")
                        error_count += 1
                
                except Exception as e:
                    error_messages.append(f"Row {row_num}: {str(e)}")
                    error_count += 1
        
        except Exception as e:
            error_messages.append(f"CSV parsing error: {str(e)}")
            error_count += 1
        
        return success_count, error_count, error_messages
    
    @staticmethod
    def validate_import_data(data: str, file_type: str) -> Tuple[bool, List[str]]:
        """
        Validate import data format.
        Returns: (is_valid, error_messages)
        """
        error_messages = []
        
        try:
            if file_type.lower() == "json":
                json_data = json.loads(data)
                
                if "words" not in json_data:
                    error_messages.append("JSON must contain a 'words' key")
                elif not isinstance(json_data["words"], list):
                    error_messages.append("'words' must be a list")
                elif len(json_data["words"]) == 0:
                    error_messages.append("No words found in JSON data")
                else:
                    # Check first few words for required fields
                    for i, word in enumerate(json_data["words"][:5]):
                        if not isinstance(word, dict):
                            error_messages.append(f"Word {i+1} is not a valid object")
                        elif "word" not in word or "definition" not in word:
                            error_messages.append(f"Word {i+1} missing required fields")
            
            elif file_type.lower() == "csv":
                csv_file = StringIO(data)
                reader = csv.DictReader(csv_file)
                
                if not reader.fieldnames:
                    error_messages.append("CSV file appears to be empty")
                elif "word" not in reader.fieldnames or "definition" not in reader.fieldnames:
                    error_messages.append("CSV must contain 'word' and 'definition' columns")
                else:
                    # Count rows
                    row_count = sum(1 for _ in reader)
                    if row_count == 0:
                        error_messages.append("No data rows found in CSV")
            
            else:
                error_messages.append("Unsupported file type")
        
        except json.JSONDecodeError:
            error_messages.append("Invalid JSON format")
        except Exception as e:
            error_messages.append(f"Validation error: {str(e)}")
        
        return len(error_messages) == 0, error_messages
