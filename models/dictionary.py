"""
Dictionary model for managing dictionary collections.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from utils.imports import ObjectId
from database.connection import get_collection
import logging

class Dictionary:
    """Model for managing dictionary collections."""
    
    def __init__(self, name: str, user_id: ObjectId, description: str = "", _id: ObjectId = None,
                 created_at: datetime = None, updated_at: datetime = None,
                 word_count: int = 0):
        self._id = _id
        self.name = name
        self.user_id = user_id
        self.description = description
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.word_count = word_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dictionary object to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "word_count": self.word_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dictionary':
        """Create Dictionary object from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            name=data["name"],
            user_id=data["user_id"],
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            word_count=data.get("word_count", 0)
        )
    
    def save(self) -> bool:
        """Save dictionary to database."""
        try:
            collection = get_collection("dictionaries")
            if collection is None:
                logging.error("Database connection failed")
                return False
            
            self.updated_at = datetime.now()
            
            if self._id is None:
                # Insert new dictionary
                result = collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                return True
            else:
                # Update existing dictionary
                result = collection.update_one(
                    {"_id": self._id},
                    {"$set": self.to_dict()}
                )
                return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error saving dictionary: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete dictionary and all its words."""
        try:
            if self._id is None:
                return False
            
            # Delete all words in this dictionary first
            words_collection = get_collection("words")
            if words_collection:
                words_collection.delete_many({"dictionary_id": self._id})
            
            # Delete the dictionary
            collection = get_collection("dictionaries")
            if collection is None:
                return False
            
            result = collection.delete_one({"_id": self._id})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting dictionary: {e}")
            return False
    
    def update_word_count(self) -> bool:
        """Update the word count for this dictionary."""
        try:
            words_collection = get_collection("words")
            if words_collection is None:
                return False
            
            count = words_collection.count_documents({"dictionary_id": self._id})
            self.word_count = count
            return self.save()
        except Exception as e:
            logging.error(f"Error updating word count: {e}")
            return False
    
    @staticmethod
    def get_all() -> List['Dictionary']:
        """Get all dictionaries from database."""
        try:
            collection = get_collection("dictionaries")
            if collection is None:
                return []

            dictionaries = []
            for doc in collection.find().sort("name", 1):
                dictionaries.append(Dictionary.from_dict(doc))
            return dictionaries
        except Exception as e:
            logging.error(f"Error fetching dictionaries: {e}")
            return []

    @staticmethod
    def get_by_user(user_id: ObjectId) -> List['Dictionary']:
        """Get all dictionaries for a specific user."""
        try:
            collection = get_collection("dictionaries")
            if collection is None:
                return []

            dictionaries = []
            for doc in collection.find({"user_id": user_id}).sort("name", 1):
                dictionaries.append(Dictionary.from_dict(doc))
            return dictionaries
        except Exception as e:
            logging.error(f"Error fetching user dictionaries: {e}")
            return []
    
    @staticmethod
    def get_by_id(dictionary_id: ObjectId) -> Optional['Dictionary']:
        """Get dictionary by ID."""
        try:
            collection = get_collection("dictionaries")
            if collection is None:
                return None
            
            doc = collection.find_one({"_id": dictionary_id})
            if doc:
                return Dictionary.from_dict(doc)
            return None
        except Exception as e:
            logging.error(f"Error fetching dictionary: {e}")
            return None
    
    @staticmethod
    def get_by_name(name: str) -> Optional['Dictionary']:
        """Get dictionary by name."""
        try:
            collection = get_collection("dictionaries")
            if collection is None:
                return None
            
            doc = collection.find_one({"name": name})
            if doc:
                return Dictionary.from_dict(doc)
            return None
        except Exception as e:
            logging.error(f"Error fetching dictionary: {e}")
            return None
    
    @staticmethod
    def name_exists(name: str, exclude_id: ObjectId = None) -> bool:
        """Check if dictionary name already exists."""
        try:
            collection = get_collection("dictionaries")
            if collection is None:
                return False
            
            query = {"name": name}
            if exclude_id:
                query["_id"] = {"$ne": exclude_id}
            
            return collection.count_documents(query) > 0
        except Exception as e:
            logging.error(f"Error checking dictionary name: {e}")
            return False
