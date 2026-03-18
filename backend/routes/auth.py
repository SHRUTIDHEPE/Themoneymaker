from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from typing import Annotated
import logging

# Make sure these imports work
from models.mongo_models import User
from schemas.auth import UserCreate, UserOut, Token
from utils.auth import get_password_hash, verify_password, create_access_token
from database.mongodb import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        
        # Check if database is connected
        if not db.is_connected:
            logger.error("Database is not connected")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        # Check if user already exists
        existing_user = await User.find_one({"email": user_data.email})
        if existing_user:
            logger.warning(f"Registration failed: Email {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        logger.info(f"Password hashed successfully for {user_data.email}")
        
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        await new_user.insert()
        logger.info(f"User {user_data.email} saved to database with ID: {new_user.id}")
        
        return new_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        # Log any other errors
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )