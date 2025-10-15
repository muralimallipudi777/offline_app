"""
Word management router.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, Response
from typing import List, Optional
from schemas.dictionary import (
    WordCreate, WordUpdate, WordResponse, WordSearch, 
    SearchResponse, ImportData, ExportFormat
)
from utils.auth import get_current_active_user
from utils.import_export import ImportExportManager
from models.user import User
from models.dictionary import Dictionary
from models.word import Word
from utils.imports import ObjectId
import logging

router = APIRouter()

@router.post("/{dictionary_id}/words", response_model=WordResponse, status_code=status.HTTP_201_CREATED)
async def create_word(
    dictionary_id: str,
    word_data: WordCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new word in a dictionary."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )
        
        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if word already exists
        if Word.word_exists(word_data.word, ObjectId(dictionary_id)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Word already exists in this dictionary"
            )
        
        word = Word(
            word=word_data.word,
            definition=word_data.definition,
            dictionary_id=ObjectId(dictionary_id),
            user_id=current_user._id,
            pronunciation=word_data.pronunciation or "",
            examples=word_data.examples or [],
            categories=word_data.categories or [],
            notes=word_data.notes or ""
        )
        
        if word.save():
            # Update dictionary word count
            dictionary.update_word_count()
            
            return WordResponse(
                id=str(word._id),
                word=word.word,
                definition=word.definition,
                pronunciation=word.pronunciation,
                examples=word.examples,
                categories=word.categories,
                notes=word.notes,
                created_at=word.created_at.isoformat(),
                updated_at=word.updated_at.isoformat()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create word"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Word creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create word"
        )

@router.get("/{dictionary_id}/words", response_model=List[WordResponse])
async def get_dictionary_words(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of words to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of words to return")
):
    """Get all words in a dictionary."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )
        
        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        words = Word.get_by_dictionary(ObjectId(dictionary_id), limit=limit, skip=skip)
        return [
            WordResponse(
                id=str(w._id),
                word=w.word,
                definition=w.definition,
                pronunciation=w.pronunciation,
                examples=w.examples,
                categories=w.categories,
                notes=w.notes,
                created_at=w.created_at.isoformat(),
                updated_at=w.updated_at.isoformat()
            )
            for w in words
        ]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching words: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch words"
        )

@router.get("/{dictionary_id}/words/{word_id}", response_model=WordResponse)
async def get_word(
    dictionary_id: str,
    word_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific word."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )
        
        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        word = Word.get_by_id(ObjectId(word_id))
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found"
            )
        
        # Check if word belongs to the dictionary
        if word.dictionary_id != ObjectId(dictionary_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found in this dictionary"
            )
        
        return WordResponse(
            id=str(word._id),
            word=word.word,
            definition=word.definition,
            pronunciation=word.pronunciation,
            examples=word.examples,
            categories=word.categories,
            notes=word.notes,
            created_at=word.created_at.isoformat(),
            updated_at=word.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching word: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch word"
        )

@router.put("/{dictionary_id}/words/{word_id}", response_model=WordResponse)
async def update_word(
    dictionary_id: str,
    word_id: str,
    word_data: WordUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a word."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )
        
        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        word = Word.get_by_id(ObjectId(word_id))
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found"
            )
        
        # Check if word belongs to the dictionary
        if word.dictionary_id != ObjectId(dictionary_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found in this dictionary"
            )
        
        # Update fields
        if word_data.word is not None:
            # Check if new word conflicts with existing words
            if Word.word_exists(word_data.word, ObjectId(dictionary_id), exclude_id=word._id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Word already exists in this dictionary"
                )
            word.word = word_data.word.strip().lower()
        
        if word_data.definition is not None:
            word.definition = word_data.definition.strip()
        if word_data.pronunciation is not None:
            word.pronunciation = word_data.pronunciation.strip()
        if word_data.examples is not None:
            word.examples = word_data.examples
        if word_data.categories is not None:
            word.categories = word_data.categories
        if word_data.notes is not None:
            word.notes = word_data.notes.strip()
        
        if word.save():
            return WordResponse(
                id=str(word._id),
                word=word.word,
                definition=word.definition,
                pronunciation=word.pronunciation,
                examples=word.examples,
                categories=word.categories,
                notes=word.notes,
                created_at=word.created_at.isoformat(),
                updated_at=word.updated_at.isoformat()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update word"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating word: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update word"
        )

@router.delete("/{dictionary_id}/words/{word_id}")
async def delete_word(
    dictionary_id: str,
    word_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a word."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )

        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        word = Word.get_by_id(ObjectId(word_id))
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found"
            )

        # Check if word belongs to the dictionary
        if word.dictionary_id != ObjectId(dictionary_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Word not found in this dictionary"
            )

        if word.delete():
            # Update dictionary word count
            dictionary.update_word_count()
            return {"message": "Word deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete word"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting word: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete word"
        )

@router.post("/{dictionary_id}/search", response_model=SearchResponse)
async def search_words(
    dictionary_id: str,
    search_data: WordSearch,
    current_user: User = Depends(get_current_active_user)
):
    """Search words in a dictionary."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )

        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        words = Word.search_words(
            ObjectId(dictionary_id),
            search_data.query,
            search_data.search_type
        )

        word_responses = [
            WordResponse(
                id=str(w._id),
                word=w.word,
                definition=w.definition,
                pronunciation=w.pronunciation,
                examples=w.examples,
                categories=w.categories,
                notes=w.notes,
                created_at=w.created_at.isoformat(),
                updated_at=w.updated_at.isoformat()
            )
            for w in words
        ]

        return SearchResponse(
            words=word_responses,
            total_count=len(word_responses),
            query=search_data.query,
            search_type=search_data.search_type
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error searching words: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search words"
        )

@router.post("/{dictionary_id}/import")
async def import_words(
    dictionary_id: str,
    import_data: ImportData,
    current_user: User = Depends(get_current_active_user)
):
    """Import words into a dictionary."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )

        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Validate import data
        is_valid, validation_errors = ImportExportManager.validate_import_data(
            import_data.data, import_data.format
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data format: {'; '.join(validation_errors)}"
            )

        # Import data
        if import_data.format.lower() == "json":
            success_count, error_count, error_messages = ImportExportManager.import_from_json(
                import_data.data, ObjectId(dictionary_id)
            )
        elif import_data.format.lower() == "csv":
            success_count, error_count, error_messages = ImportExportManager.import_from_csv(
                import_data.data, ObjectId(dictionary_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format. Use 'json' or 'csv'"
            )

        # Update dictionary word count
        dictionary.update_word_count()

        return {
            "message": f"Import completed",
            "success_count": success_count,
            "error_count": error_count,
            "errors": error_messages[:10] if error_messages else []  # Limit errors shown
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error importing words: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import words"
        )

@router.get("/{dictionary_id}/export")
async def export_dictionary(
    dictionary_id: str,
    format: str = Query(..., description="Export format: json or csv"),
    current_user: User = Depends(get_current_active_user)
):
    """Export dictionary data."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )

        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        if format.lower() == "json":
            data = ImportExportManager.export_dictionary_to_json(dictionary)
            media_type = "application/json"
            filename = f"{dictionary.name}_dictionary.json"
        elif format.lower() == "csv":
            data = ImportExportManager.export_dictionary_to_csv(dictionary)
            media_type = "text/csv"
            filename = f"{dictionary.name}_words.csv"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format. Use 'json' or 'csv'"
            )

        if not data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export data"
            )

        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error exporting dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export dictionary"
        )

@router.get("/{dictionary_id}/categories", response_model=List[str])
async def get_categories(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all categories used in a dictionary."""
    try:
        # Get and validate dictionary
        dictionary = Dictionary.get_by_id(ObjectId(dictionary_id))
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dictionary not found"
            )

        # Check if user owns this dictionary
        if dictionary.user_id != current_user._id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        categories = Word.get_categories(ObjectId(dictionary_id))
        return categories
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )
