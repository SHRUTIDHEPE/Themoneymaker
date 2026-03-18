from beanie import Document, Indexed
from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class User(Document):
    """User document model"""
    email: str = Indexed(unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        use_state_management = True
        
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashed_password_here",
                "created_at": "2024-01-01T00:00:00"
            }
        }

class Holding(BaseModel):
    """Embedded holding document"""
    symbol: str
    shares: float
    purchase_price: float
    purchase_date: datetime

class Portfolio(Document):
    """Portfolio document model"""
    user_id: str
    name: str
    holdings: List[Holding] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "portfolios"
        use_state_management = True

class StockPrice(Document):
    """Stock price document model"""
    symbol: str = Indexed()
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    class Settings:
        name = "stock_prices"
        use_state_management = True
        indexes = [
            [("symbol", 1), ("date", -1)],
        ]

class AlertCondition(str, Enum):
    ABOVE = "above"
    BELOW = "below"

class Alert(Document):
    """Alert document model"""
    user_id: str
    symbol: str
    target_price: float
    condition: AlertCondition
    is_active: bool = True
    triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "alerts"
        use_state_management = True