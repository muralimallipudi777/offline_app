"""
Simple test script for the offline dictionary app.
Run this to test basic functionality.
"""

import unittest
from datetime import datetime
from utils.imports import ObjectId
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dictionary import Dictionary
from models.word import Word
from database.connection import db_connection

class TestDictionaryApp(unittest.TestCase):
    """Test cases for the dictionary app."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure database connection
        if not db_connection.is_connected():
            self.skipTest("Database not connected")
        
        # Create a test dictionary
        self.test_dict = Dictionary(
            name="Test Dictionary",
            description="A dictionary for testing"
        )
        self.assertTrue(self.test_dict.save())
    
    def tearDown(self):
        """Clean up after tests."""
        # Delete test dictionary and all its words
        if hasattr(self, 'test_dict') and self.test_dict._id:
            self.test_dict.delete()
    
    def test_dictionary_creation(self):
        """Test dictionary creation."""
        # Test dictionary was created
        self.assertIsNotNone(self.test_dict._id)
        self.assertEqual(self.test_dict.name, "Test Dictionary")
        self.assertEqual(self.test_dict.word_count, 0)
    
    def test_word_creation(self):
        """Test word creation."""
        word = Word(
            word="test",
            definition="A procedure for critical evaluation",
            dictionary_id=self.test_dict._id,
            pronunciation="/test/",
            examples=["This is a test"],
            categories=["noun"],
            notes="Test word"
        )
        
        # Save word
        self.assertTrue(word.save())
        self.assertIsNotNone(word._id)
        
        # Check word exists
        self.assertTrue(Word.word_exists("test", self.test_dict._id))
        
        # Update dictionary word count
        self.test_dict.update_word_count()
        self.assertEqual(self.test_dict.word_count, 1)
    
    def test_word_search(self):
        """Test word search functionality."""
        # Add test words
        words_data = [
            ("apple", "A round fruit"),
            ("application", "A computer program"),
            ("apply", "To put to use")
        ]
        
        for word_text, definition in words_data:
            word = Word(
                word=word_text,
                definition=definition,
                dictionary_id=self.test_dict._id
            )
            word.save()
        
        # Test word search
        results = Word.search_words(self.test_dict._id, "app", "word")
        self.assertEqual(len(results), 3)  # All words contain "app"
        
        # Test definition search
        results = Word.search_words(self.test_dict._id, "fruit", "definition")
        self.assertEqual(len(results), 1)  # Only "apple" has "fruit" in definition
    
    def test_duplicate_word_prevention(self):
        """Test that duplicate words are prevented."""
        word1 = Word(
            word="duplicate",
            definition="First definition",
            dictionary_id=self.test_dict._id
        )
        self.assertTrue(word1.save())
        
        # Try to create duplicate
        word2 = Word(
            word="duplicate",
            definition="Second definition",
            dictionary_id=self.test_dict._id
        )
        
        # Check that duplicate is detected
        self.assertTrue(Word.word_exists("duplicate", self.test_dict._id))

def run_basic_tests():
    """Run basic functionality tests."""
    print("🧪 Running basic tests for Offline Dictionary App...")
    
    # Check database connection
    print("📡 Checking database connection...")
    if db_connection.is_connected():
        print("✅ Database connected successfully!")
    else:
        print("❌ Database connection failed!")
        print("Please ensure MongoDB is running and check your .env file.")
        return False
    
    # Run unit tests
    print("\n🔬 Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    return True

if __name__ == "__main__":
    run_basic_tests()
