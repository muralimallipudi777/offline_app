"""
Centralized import handling for the offline dictionary app.
This module handles all problematic imports with proper fallbacks.
"""

# Try to import pymongo and related modules
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    print("Warning: PyMongo not available. Database functionality will be limited.")
    MongoClient = None
    ConnectionFailure = Exception
    ServerSelectionTimeoutError = Exception
    PYMONGO_AVAILABLE = False

# Try to import bson
try:
    from bson import ObjectId
    BSON_AVAILABLE = True
except ImportError:
    print("Warning: BSON not available. Using string fallback for ObjectId.")
    ObjectId = str
    BSON_AVAILABLE = False

# Export all imports for use in other modules
__all__ = [
    'MongoClient', 'ConnectionFailure', 'ServerSelectionTimeoutError', 'PYMONGO_AVAILABLE',
    'ObjectId', 'BSON_AVAILABLE'
]
