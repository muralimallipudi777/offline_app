"""
Dictionary management router.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from schemas.dictionary import DictionaryCreate, DictionaryUpdate, DictionaryResponse
from utils.auth import get_current_active_user
from models.user import User
from models.dictionary import Dictionary
from utils.imports import ObjectId
import logging

router = APIRouter()

@router.post("/", response_model=DictionaryResponse, status_code=status.HTTP_201_CREATED)
async def create_dictionary(
    dictionary_data: DictionaryCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new dictionary."""
    try:
        # Check if dictionary name already exists for this user
        existing_dicts = Dictionary.get_by_user(current_user._id)
        if any(d.name.lower() == dictionary_data.name.lower() for d in existing_dicts):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dictionary name already exists"
            )
        
        dictionary = Dictionary(
            name=dictionary_data.name,
            user_id=current_user._id,
            description=dictionary_data.description or ""
        )
        
        if dictionary.save():
            return DictionaryResponse(
                id=str(dictionary._id),
                name=dictionary.name,
                description=dictionary.description,
                word_count=dictionary.word_count,
                created_at=dictionary.created_at.isoformat(),
                updated_at=dictionary.updated_at.isoformat()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create dictionary"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Dictionary creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dictionary"
        )

@router.get("/", response_model=List[DictionaryResponse])
async def get_user_dictionaries(current_user: User = Depends(get_current_active_user)):
    """Get all dictionaries for the current user."""
    try:
        dictionaries = Dictionary.get_by_user(current_user._id)
        return [
            DictionaryResponse(
                id=str(d._id),
                name=d.name,
                description=d.description,
                word_count=d.word_count,
                created_at=d.created_at.isoformat(),
                updated_at=d.updated_at.isoformat()
            )
            for d in dictionaries
        ]
    except Exception as e:
        logging.error(f"Error fetching dictionaries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dictionaries"
        )

@router.get("/{dictionary_id}", response_model=DictionaryResponse)
async def get_dictionary(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific dictionary."""
    try:
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
        
        return DictionaryResponse(
            id=str(dictionary._id),
            name=dictionary.name,
            description=dictionary.description,
            word_count=dictionary.word_count,
            created_at=dictionary.created_at.isoformat(),
            updated_at=dictionary.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dictionary"
        )

@router.put("/{dictionary_id}", response_model=DictionaryResponse)
async def update_dictionary(
    dictionary_id: str,
    dictionary_data: DictionaryUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a dictionary."""
    try:
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
        
        # Update fields
        if dictionary_data.name is not None:
            # Check if new name conflicts with existing dictionaries
            existing_dicts = Dictionary.get_by_user(current_user._id)
            if any(d.name.lower() == dictionary_data.name.lower() and d._id != dictionary._id for d in existing_dicts):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Dictionary name already exists"
                )
            dictionary.name = dictionary_data.name
        
        if dictionary_data.description is not None:
            dictionary.description = dictionary_data.description
        
        if dictionary.save():
            return DictionaryResponse(
                id=str(dictionary._id),
                name=dictionary.name,
                description=dictionary.description,
                word_count=dictionary.word_count,
                created_at=dictionary.created_at.isoformat(),
                updated_at=dictionary.updated_at.isoformat()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update dictionary"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dictionary"
        )

@router.delete("/{dictionary_id}")
async def delete_dictionary(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a dictionary and all its words."""
    try:
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
        
        if dictionary.delete():
            return {"message": "Dictionary deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete dictionary"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dictionary"
        )
