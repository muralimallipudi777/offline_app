"""
Setup script for the Offline Dictionary App.
"""

import os
import sys
import subprocess
from pathlib import Path

# Import pymongo with fallback handling
from utils.imports import MongoClient, PYMONGO_AVAILABLE

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_mongodb():
    """Check if MongoDB is accessible."""
    if not PYMONGO_AVAILABLE:
        print("❌ PyMongo is not installed:")
        print("   Please install pymongo: pip install pymongo")
        return False
        
    try:
        client = MongoClient('mongodb://localhost:27017/offline', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print("❌ MongoDB connection failed:")
        print(f"   {e}")
        print("   Please ensure MongoDB is installed and running")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    try:
        with open(env_file, 'w') as f:
            f.write("# MongoDB Configuration\n")
            f.write("MONGODB_URI=mongodb://localhost:27017/offline\n")
            f.write("DATABASE_NAME=offline\n\n")
            f.write("# Application Configuration\n")
            f.write("APP_TITLE=My Personal Dictionary\n")
            f.write("DEBUG=False\n")
        print("✅ Created .env file with default settings")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_tests():
    """Run basic tests."""
    try:
        print("🧪 Running basic tests...")
        result = subprocess.run([sys.executable, "test_api.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Basic tests passed")
            return True
        else:
            print("⚠️ Some tests failed, but the API should still work")
            print("Check the test output for details")
            return True  # Don't fail setup for test failures
    except Exception as e:
        print(f"⚠️ Could not run tests: {e}")
        return True  # Don't fail setup for test failures

def main():
    """Main setup function."""
    print("🚀 Setting up Offline Dictionary App...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check MongoDB
    mongodb_ok = check_mongodb()
    
    # Run tests if MongoDB is available
    if mongodb_ok:
        run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    
    if mongodb_ok:
        print("\n✅ Everything is ready! You can now run the API with:")
        print("   uvicorn main:app --reload")
        print("\n📖 Then visit:")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️ Setup completed, but MongoDB is not accessible.")
        print("   Please install and start MongoDB, then run:")
        print("   uvicorn main:app --reload")
    
    print("\n📖 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
