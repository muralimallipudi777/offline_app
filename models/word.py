"""
Word model for managing individual word entries.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from utils.imports import ObjectId
from database.connection import get_collection
import logging

class Word:
    """Model for managing individual word entries."""
    
    def __init__(self, word: str, definition: str, dictionary_id: ObjectId,
                 user_id: ObjectId, pronunciation: str = "", examples: List[str] = None,
                 categories: List[str] = None, notes: str = "",
                 _id: ObjectId = None, created_at: datetime = None,
                 updated_at: datetime = None):
        self._id = _id
        self.word = word.strip().lower()  # Store in lowercase for consistency
        self.definition = definition.strip()
        self.dictionary_id = dictionary_id
        self.user_id = user_id
        self.pronunciation = pronunciation.strip()
        self.examples = examples or []
        self.categories = categories or []
        self.notes = notes.strip()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert word object to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "word": self.word,
            "definition": self.definition,
            "dictionary_id": self.dictionary_id,
            "user_id": self.user_id,
            "pronunciation": self.pronunciation,
            "examples": self.examples,
            "categories": self.categories,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Word':
        """Create Word object from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            word=data["word"],
            definition=data["definition"],
            dictionary_id=data["dictionary_id"],
            user_id=data["user_id"],
            pronunciation=data.get("pronunciation", ""),
            examples=data.get("examples", []),
            categories=data.get("categories", []),
            notes=data.get("notes", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def save(self) -> bool:
        """Save word to database."""
        try:
            collection = get_collection("words")
            if collection is None:
                logging.error("Database connection failed")
                return False
            
            self.updated_at = datetime.now()
            
            if self._id is None:
                # Insert new word
                result = collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                
                # Update dictionary word count
                self._update_dictionary_word_count()
                return True
            else:
                # Update existing word
                result = collection.update_one(
                    {"_id": self._id},
                    {"$set": self.to_dict()}
                )
                return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error saving word: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete word from database."""
        try:
            if self._id is None:
                return False
            
            collection = get_collection("words")
            if collection is None:
                return False
            
            result = collection.delete_one({"_id": self._id})
            if result.deleted_count > 0:
                # Update dictionary word count
                self._update_dictionary_word_count()
                return True
            return False
        except Exception as e:
            logging.error(f"Error deleting word: {e}")
            return False
    
    def _update_dictionary_word_count(self):
        """Update the word count in the parent dictionary."""
        try:
            from models.dictionary import Dictionary
            dictionary = Dictionary.get_by_id(self.dictionary_id)
            if dictionary:
                dictionary.update_word_count()
        except Exception as e:
            logging.error(f"Error updating dictionary word count: {e}")
    
    @staticmethod
    def get_by_dictionary(dictionary_id: ObjectId, limit: int = None, 
                         skip: int = 0) -> List['Word']:
        """Get all words for a specific dictionary."""
        try:
            collection = get_collection("words")
            if collection is None:
                return []
            
            query = {"dictionary_id": dictionary_id}
            cursor = collection.find(query).sort("word", 1).skip(skip)
            
            if limit:
                cursor = cursor.limit(limit)
            
            words = []
            for doc in cursor:
                words.append(Word.from_dict(doc))
            return words
        except Exception as e:
            logging.error(f"Error fetching words: {e}")
            return []
    
    @staticmethod
    def search_words(dictionary_id: ObjectId, search_term: str, 
                    search_type: str = "word") -> List['Word']:
        """Search words in a dictionary."""
        try:
            collection = get_collection("words")
            if collection is None:
                return []
            
            search_term = search_term.strip().lower()
            base_query = {"dictionary_id": dictionary_id}
            
            if search_type == "word":
                # Search in word field
                query = {**base_query, "word": {"$regex": search_term, "$options": "i"}}
            elif search_type == "definition":
                # Search in definition field
                query = {**base_query, "definition": {"$regex": search_term, "$options": "i"}}
            elif search_type == "both":
                # Search in both word and definition
                query = {
                    **base_query,
                    "$or": [
                        {"word": {"$regex": search_term, "$options": "i"}},
                        {"definition": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            else:
                query = base_query
            
            words = []
            for doc in collection.find(query).sort("word", 1):
                words.append(Word.from_dict(doc))
            return words
        except Exception as e:
            logging.error(f"Error searching words: {e}")
            return []
    
    @staticmethod
    def get_by_id(word_id: ObjectId) -> Optional['Word']:
        """Get word by ID."""
        try:
            collection = get_collection("words")
            if collection is None:
                return None
            
            doc = collection.find_one({"_id": word_id})
            if doc:
                return Word.from_dict(doc)
            return None
        except Exception as e:
            logging.error(f"Error fetching word: {e}")
            return None
    
    @staticmethod
    def word_exists(word: str, dictionary_id: ObjectId, 
                   exclude_id: ObjectId = None) -> bool:
        """Check if word already exists in dictionary."""
        try:
            collection = get_collection("words")
            if collection is None:
                return False
            
            query = {"word": word.strip().lower(), "dictionary_id": dictionary_id}
            if exclude_id:
                query["_id"] = {"$ne": exclude_id}
            
            return collection.count_documents(query) > 0
        except Exception as e:
            logging.error(f"Error checking word existence: {e}")
            return False
    
    @staticmethod
    def get_categories(dictionary_id: ObjectId) -> List[str]:
        """Get all unique categories for a dictionary."""
        try:
            collection = get_collection("words")
            if collection is None:
                return []
            
            pipeline = [
                {"$match": {"dictionary_id": dictionary_id}},
                {"$unwind": "$categories"},
                {"$group": {"_id": "$categories"}},
                {"$sort": {"_id": 1}}
            ]
            
            categories = []
            for doc in collection.aggregate(pipeline):
                if doc["_id"]:  # Skip empty categories
                    categories.append(doc["_id"])
            return categories
        except Exception as e:
            logging.error(f"Error fetching categories: {e}")
            return []
