# API Endpoints Documentation

## Base URL
```
http://localhost:8000
```

## Authentication Endpoints

### Register User
- **POST** `/api/auth/register`
- **Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

### Login
- **POST** `/api/auth/login`
- **Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
- **Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Get Current User
- **GET** `/api/auth/me`
- **Headers:** `Authorization: Bearer <token>`

### Change Password
- **POST** `/api/auth/change-password`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

## Dictionary Endpoints

### Create Dictionary
- **POST** `/api/dictionaries/`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

### Get User Dictionaries
- **GET** `/api/dictionaries/`
- **Headers:** `Authorization: Bearer <token>`

### Get Dictionary
- **GET** `/api/dictionaries/{dictionary_id}`
- **Headers:** `Authorization: Bearer <token>`

### Update Dictionary
- **PUT** `/api/dictionaries/{dictionary_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

### Delete Dictionary
- **DELETE** `/api/dictionaries/{dictionary_id}`
- **Headers:** `Authorization: Bearer <token>`

## Word Endpoints

### Create Word
- **POST** `/api/words/{dictionary_id}/words`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "word": "string",
  "definition": "string",
  "pronunciation": "string",
  "examples": ["string"],
  "categories": ["string"],
  "notes": "string"
}
```

### Get Dictionary Words
- **GET** `/api/words/{dictionary_id}/words?skip=0&limit=100`
- **Headers:** `Authorization: Bearer <token>`

### Get Word
- **GET** `/api/words/{dictionary_id}/words/{word_id}`
- **Headers:** `Authorization: Bearer <token>`

### Update Word
- **PUT** `/api/words/{dictionary_id}/words/{word_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Body:** (same as create word, all fields optional)

### Delete Word
- **DELETE** `/api/words/{dictionary_id}/words/{word_id}`
- **Headers:** `Authorization: Bearer <token>`

### Search Words
- **POST** `/api/words/{dictionary_id}/search`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "query": "string",
  "search_type": "word|definition|both"
}
```

### Import Words
- **POST** `/api/words/{dictionary_id}/import`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "data": "string (JSON or CSV data)",
  "format": "json|csv"
}
```

### Export Dictionary
- **GET** `/api/words/{dictionary_id}/export?format=json|csv`
- **Headers:** `Authorization: Bearer <token>`

### Get Categories
- **GET** `/api/words/{dictionary_id}/categories`
- **Headers:** `Authorization: Bearer <token>`

## Status Endpoints

### Health Check
- **GET** `/health`

### Root
- **GET** `/`

## Interactive Documentation

Visit these URLs when the server is running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Example Usage

1. Register and login to get a token
2. Create a dictionary
3. Add words to the dictionary
4. Search and manage your words
5. Export your dictionary for backup

All endpoints require authentication except for registration, login, health check, and root.
