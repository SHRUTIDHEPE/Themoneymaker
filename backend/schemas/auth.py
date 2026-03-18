from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "password": "password123"
            }
        }

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """Schema for user response (excludes password)"""
    id: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "65abc123def456...",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
        }

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None