from beanie import Document, Indexed
from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class User(Document):
    email: Indexed(str, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashed_password_here",
                "created_at": "2024-01-01T00:00:00"
            }
        }

class Holding(BaseModel):
    symbol: str
    shares: float
    purchase_price: float
    purchase_date: datetime

class Portfolio(Document):
    user_id: str
    name: str
    holdings: List[Holding] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "portfolios"

class StockPrice(Document):
    symbol: Indexed(str)
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    class Settings:
        name = "stock_prices"
        indexes = [
            [("symbol", 1), ("date", -1)],
        ]

class AlertCondition(str, Enum):
    ABOVE = "above"
    BELOW = "below"

class Alert(Document):
    user_id: str
    symbol: str
    target_price: float
    condition: AlertCondition
    is_active: bool = True
    triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "alerts"