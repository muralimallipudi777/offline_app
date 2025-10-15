# Offline Dictionary API

A personal dictionary REST API built with FastAPI, Python, and MongoDB that allows users to create and manage their own custom dictionaries with authentication.

## Features

- 🔐 **User Authentication** - JWT-based registration and login
- 📚 **Multiple Dictionaries** - Create and manage multiple custom dictionaries
- 📝 **Word Management** - Add, edit, and delete words with definitions, pronunciations, examples
- 🔍 **Advanced Search** - Search by word name, definition, or both
- 📤 **Import/Export** - Import/export dictionaries in JSON or CSV format
- 🏷️ **Categories** - Organize words with custom categories
- 🔒 **User Isolation** - Each user's data is completely separate
- 📖 **API Documentation** - Interactive API docs with Swagger UI
- 🗄️ **MongoDB Storage** - Reliable local database storage

## Quick Setup

### Option 1: Automated Setup
```bash
python setup.py
```

### Option 2: Manual Setup

1. **Install MongoDB locally**
   - Download from [MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Start MongoDB service

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set a secure SECRET_KEY for JWT tokens.

5. **Run the API server:**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Project Structure

```
offline-dictionary/
├── main.py               # FastAPI main application
├── routers/              # API route handlers
│   ├── auth.py          # Authentication endpoints
│   ├── dictionaries.py # Dictionary management
│   └── words.py         # Word management
├── models/               # Database models
│   ├── user.py          # User model
│   ├── dictionary.py    # Dictionary model
│   └── word.py          # Word model
├── schemas/              # Pydantic schemas
│   ├── auth.py          # Auth request/response models
│   └── dictionary.py    # Dictionary/word schemas
├── database/
│   └── connection.py    # MongoDB connection utilities
├── utils/
│   ├── auth.py          # JWT authentication utilities
│   └── import_export.py # Import/export functionality
├── requirements.txt
├── sample_data.json     # Sample data for testing
├── sample_data.csv      # Sample CSV data
└── README.md
```

## API Usage

### 1. Start the API Server
```bash
uvicorn main:app --reload
```

### 2. Register a User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Login to Get Token
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 4. Create a Dictionary
```bash
curl -X POST "http://localhost:8000/api/dictionaries/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My English Dictionary",
    "description": "Personal English vocabulary"
  }'
```

### 5. Add Words
```bash
curl -X POST "http://localhost:8000/api/words/DICTIONARY_ID/words" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "word": "serendipity",
    "definition": "The occurrence of events by chance in a happy way",
    "pronunciation": "/ˌserənˈdipədē/",
    "examples": ["It was pure serendipity that we met"],
    "categories": ["noun", "abstract"]
  }'
```

### 6. Interactive Documentation
Visit http://localhost:8000/docs for interactive API documentation where you can test all endpoints.

## Sample Data

The project includes sample data files:
- `sample_data.json` - JSON format with 5 sample words
- `sample_data.csv` - CSV format with 5 sample words

You can import these to test the application functionality.

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is installed and running
- Check that the MongoDB service is started
- Verify the connection string in `.env` file
- Default connection: `mongodb://localhost:27017/offline`

### Application Issues
- Run `python test_app.py` to check basic functionality
- Check the Streamlit logs for error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Import/Export Issues
- Ensure your CSV has required columns: `word`, `definition`
- Check JSON format matches the sample structure
- Verify file encoding is UTF-8
