"""
Authentication router for user registration and login.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from datetime import timedelta
from schemas.auth import UserRegister, UserLogin, Token, UserResponse, PasswordChange
from utils.auth import AuthManager, get_current_active_user
from models.user import User
import logging

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user."""
    try:
        user = AuthManager.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return UserResponse(**user.to_public_dict())
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Authenticate user and return access token."""
    user = AuthManager.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = AuthManager.create_access_token(
        data={"sub": str(user._id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(**current_user.to_public_dict())

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user)
):
    """Change user password."""
    # Verify current password
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Set new password
    current_user.set_password(password_data.new_password)
    if current_user.save():
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.delete("/account")
async def delete_account(current_user: User = Depends(get_current_active_user)):
    """Delete user account and all associated data."""
    try:
        # Delete all user's dictionaries and words
        from models.dictionary import Dictionary
        from models.word import Word
        
        # Get user's dictionaries
        dictionaries = Dictionary.get_by_user(current_user._id)
        
        # Delete all words in user's dictionaries
        for dictionary in dictionaries:
            words = Word.get_by_dictionary(dictionary._id)
            for word in words:
                word.delete()
            dictionary.delete()
        
        # Delete user account
        if current_user.delete():
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account"
            )
    except Exception as e:
        logging.error(f"Account deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
