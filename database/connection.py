"""
MongoDB connection utilities for the offline dictionary app.
"""

import os
from utils.imports import MongoClient, ConnectionFailure, ServerSelectionTimeoutError, PYMONGO_AVAILABLE
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """Singleton class for managing MongoDB connection."""
    
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Establish connection to MongoDB."""
        if not PYMONGO_AVAILABLE:
            logging.error("PyMongo is not available. Please install pymongo: pip install pymongo")
            self._client = None
            self._database = None
            return
            
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/offline')
            database_name = os.getenv('DATABASE_NAME', 'offline')
            
            self._client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            
            # Test the connection
            self._client.admin.command('ping')
            self._database = self._client[database_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            logging.error("Please ensure MongoDB is running and accessible.")
            self._client = None
            self._database = None
    
    def _create_indexes(self):
        """Create database indexes for better query performance."""
        if self._database is not None:
            # Index for dictionaries collection
            self._database.dictionaries.create_index("name", unique=True)
            self._database.dictionaries.create_index("created_at")
            
            # Indexes for words collection
            self._database.words.create_index([("dictionary_id", 1), ("word", 1)], unique=True)
            self._database.words.create_index("word")
            self._database.words.create_index("dictionary_id")
            self._database.words.create_index([("word", "text"), ("definition", "text")])
    
    def get_database(self):
        """Get the database instance."""
        if self._database is None:
            self.connect()
        return self._database
    
    def get_collection(self, collection_name):
        """Get a specific collection."""
        db = self.get_database()
        if db is not None:
            return db[collection_name]
        return None
    
    def is_connected(self):
        """Check if database is connected."""
        return self._database is not None
    
    def close(self):
        """Close the database connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None

# Global database instance
db_connection = DatabaseConnection()

def get_db():
    """Get database instance."""
    return db_connection.get_database()

def get_collection(collection_name):
    """Get a specific collection."""
    return db_connection.get_collection(collection_name)
