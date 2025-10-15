"""
API testing script for the Offline Dictionary API.
"""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:8000"

class APITester:
    """Test the Dictionary API endpoints."""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.dictionary_id: Optional[str] = None
        self.word_id: Optional[str] = None
    
    def test_health(self):
        """Test health endpoint."""
        print("🔍 Testing health endpoint...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
            print(f"   Status: {response.status_code}")
        print()
    
    def test_register(self):
        """Test user registration."""
        print("👤 Testing user registration...")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        if response.status_code == 201:
            print("✅ User registration successful")
            user_data = response.json()
            self.user_id = user_data["id"]
            print(f"   User ID: {self.user_id}")
        else:
            print("❌ User registration failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def test_login(self):
        """Test user login."""
        print("🔑 Testing user login...")
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        if response.status_code == 200:
            print("✅ User login successful")
            token_data = response.json()
            self.token = token_data["access_token"]
            print(f"   Token received: {self.token[:20]}...")
        else:
            print("❌ User login failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def test_create_dictionary(self):
        """Test dictionary creation."""
        print("📚 Testing dictionary creation...")
        if not self.token:
            print("❌ No token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "name": "Test Dictionary",
            "description": "A dictionary for API testing"
        }
        response = requests.post(f"{BASE_URL}/api/dictionaries/", json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Dictionary creation successful")
            dict_data = response.json()
            self.dictionary_id = dict_data["id"]
            print(f"   Dictionary ID: {self.dictionary_id}")
        else:
            print("❌ Dictionary creation failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def test_add_word(self):
        """Test adding a word."""
        print("📝 Testing word creation...")
        if not self.token or not self.dictionary_id:
            print("❌ Missing token or dictionary ID")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "word": "serendipity",
            "definition": "The occurrence of events by chance in a happy way",
            "pronunciation": "/ˌserənˈdipədē/",
            "examples": ["It was pure serendipity that we met"],
            "categories": ["noun", "abstract"],
            "notes": "A beautiful word"
        }
        response = requests.post(
            f"{BASE_URL}/api/words/{self.dictionary_id}/words",
            json=data,
            headers=headers
        )
        if response.status_code == 201:
            print("✅ Word creation successful")
            word_data = response.json()
            self.word_id = word_data["id"]
            print(f"   Word ID: {self.word_id}")
            print(f"   Word: {word_data['word']}")
        else:
            print("❌ Word creation failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def test_search_words(self):
        """Test word search."""
        print("🔍 Testing word search...")
        if not self.token or not self.dictionary_id:
            print("❌ Missing token or dictionary ID")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "query": "serendipity",
            "search_type": "word"
        }
        response = requests.post(
            f"{BASE_URL}/api/words/{self.dictionary_id}/search",
            json=data,
            headers=headers
        )
        if response.status_code == 200:
            print("✅ Word search successful")
            search_data = response.json()
            print(f"   Found {search_data['total_count']} words")
            if search_data['words']:
                print(f"   First result: {search_data['words'][0]['word']}")
        else:
            print("❌ Word search failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def test_export_dictionary(self):
        """Test dictionary export."""
        print("📤 Testing dictionary export...")
        if not self.token or not self.dictionary_id:
            print("❌ Missing token or dictionary ID")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{BASE_URL}/api/words/{self.dictionary_id}/export?format=json",
            headers=headers
        )
        if response.status_code == 200:
            print("✅ Dictionary export successful")
            print(f"   Export size: {len(response.content)} bytes")
            # Try to parse as JSON
            try:
                data = response.json()
                print(f"   Dictionary: {data.get('dictionary', {}).get('name', 'Unknown')}")
                print(f"   Words: {len(data.get('words', []))}")
            except:
                print("   Export format: CSV")
        else:
            print("❌ Dictionary export failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def test_get_user_info(self):
        """Test getting current user info."""
        print("👤 Testing user info retrieval...")
        if not self.token:
            print("❌ No token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ User info retrieval successful")
            user_data = response.json()
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
        else:
            print("❌ User info retrieval failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
        print()
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting API tests...\n")
        
        self.test_health()
        self.test_register()
        self.test_login()
        self.test_get_user_info()
        self.test_create_dictionary()
        self.test_add_word()
        self.test_search_words()
        self.test_export_dictionary()
        
        print("🎉 API tests completed!")

def main():
    """Main function to run API tests."""
    print("Offline Dictionary API Tester")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ API server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running: uvicorn main:app --reload")
        sys.exit(1)
    
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
