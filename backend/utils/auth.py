from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Password hashing - with proper configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Set explicit rounds
)

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password):
    """Hash a password"""
    try:
        # Ensure password is string and encode properly
        if isinstance(password, str):
            password = password.encode('utf-8')
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        # Fallback hashing method
        from passlib.hash import bcrypt
        return bcrypt.hash(password)

def create_access_token(data: dict):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db):
    """Verify and decode JWT token to get current user"""
    from models.mongo_models import User
    
    credentials_exception = Exception("Could not validate credentials")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Find user in MongoDB
    user = await User.find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    return user