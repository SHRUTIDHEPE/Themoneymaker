from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class HoldingBase(BaseModel):
    """Base schema for a stock holding"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")
    shares: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Purchase price per share")
    purchase_date: datetime = Field(default_factory=datetime.utcnow)

class HoldingCreate(HoldingBase):
    """Schema for creating a holding"""
    pass

class HoldingOut(HoldingBase):
    """Schema for holding response"""
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    gain_loss: Optional[float] = None
    gain_loss_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    """Base schema for portfolio"""
    name: str = Field(..., description="Portfolio name")

class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio"""
    pass

class PortfolioOut(PortfolioBase):
    """Schema for portfolio response"""
    id: str
    user_id: str
    holdings: List[HoldingOut] = []
    total_value: float = 0
    total_cost: float = 0
    total_gain_loss: float = 0
    total_gain_loss_percentage: float = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True