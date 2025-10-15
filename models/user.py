"""
User model for authentication and user management.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from utils.imports import ObjectId
from database.connection import get_collection
from passlib.context import CryptContext
import logging

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    """Model for managing user accounts."""
    
    def __init__(self, username: str, email: str, password_hash: str = None,
                 _id: ObjectId = None, created_at: datetime = None,
                 updated_at: datetime = None, is_active: bool = True):
        self._id = _id
        self.username = username.strip().lower()
        self.email = email.strip().lower()
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_active = is_active
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for MongoDB storage."""
        data = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active
        }
        # Only include _id if it's not None (for existing users)
        if self._id is not None:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User object from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            username=data["username"],
            email=data["email"],
            password_hash=data.get("password_hash"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            is_active=data.get("is_active", True)
        )
    
    def set_password(self, password: str):
        """Hash and set password."""
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return pwd_context.verify(password, self.password_hash)
    
    def save(self) -> bool:
        """Save user to database."""
        try:
            collection = get_collection("users")
            if collection is None:
                logging.error("Database connection failed")
                return False
            
            self.updated_at = datetime.now()
            
            if self._id is None:
                # Insert new user
                result = collection.insert_one(self.to_dict())
                self._id = result.inserted_id
                return True
            else:
                # Update existing user
                result = collection.update_one(
                    {"_id": self._id},
                    {"$set": self.to_dict()}
                )
                return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error saving user: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete user from database."""
        try:
            if self._id is None:
                return False
            
            collection = get_collection("users")
            if collection is None:
                return False
            
            result = collection.delete_one({"_id": self._id})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            return False
    
    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        """Get user by username."""
        try:
            collection = get_collection("users")
            if collection is None:
                return None
            
            doc = collection.find_one({"username": username.strip().lower()})
            if doc:
                return User.from_dict(doc)
            return None
        except Exception as e:
            logging.error(f"Error fetching user by username: {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Get user by email."""
        try:
            collection = get_collection("users")
            if collection is None:
                return None
            
            doc = collection.find_one({"email": email.strip().lower()})
            if doc:
                return User.from_dict(doc)
            return None
        except Exception as e:
            logging.error(f"Error fetching user by email: {e}")
            return None
    
    @staticmethod
    def get_by_id(user_id: ObjectId) -> Optional['User']:
        """Get user by ID."""
        try:
            collection = get_collection("users")
            if collection is None:
                return None
            
            doc = collection.find_one({"_id": user_id})
            if doc:
                return User.from_dict(doc)
            return None
        except Exception as e:
            logging.error(f"Error fetching user by ID: {e}")
            return None
    
    @staticmethod
    def username_exists(username: str, exclude_id: ObjectId = None) -> bool:
        """Check if username already exists."""
        try:
            collection = get_collection("users")
            if collection is None:
                return False
            
            query = {"username": username.strip().lower()}
            if exclude_id:
                query["_id"] = {"$ne": exclude_id}
            
            return collection.count_documents(query) > 0
        except Exception as e:
            logging.error(f"Error checking username: {e}")
            return False
    
    @staticmethod
    def email_exists(email: str, exclude_id: ObjectId = None) -> bool:
        """Check if email already exists."""
        try:
            collection = get_collection("users")
            if collection is None:
                return False
            
            query = {"email": email.strip().lower()}
            if exclude_id:
                query["_id"] = {"$ne": exclude_id}
            
            return collection.count_documents(query) > 0
        except Exception as e:
            logging.error(f"Error checking email: {e}")
            return False
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert user to public dictionary (without password hash)."""
        return {
            "id": str(self._id) if self._id is not None else None,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }
