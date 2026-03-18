from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from models.mongo_models import Portfolio, User
from schemas.portfolio import PortfolioCreate, PortfolioOut, HoldingCreate, HoldingOut
from utils.auth import get_current_user
from utils.stock_api import get_current_price

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.post("", response_model=PortfolioOut)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new portfolio
    """
    portfolio = Portfolio(
        user_id=str(current_user.id),
        name=portfolio_data.name,
        holdings=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    await portfolio.insert()
    return portfolio

@router.get("", response_model=List[PortfolioOut])
async def get_all_portfolios(
    current_user: User = Depends(get_current_user)
):
    """
    Get all portfolios for current user
    """
    portfolios = await Portfolio.find(
        Portfolio.user_id == str(current_user.id)
    ).to_list()
    
    # Calculate totals for each portfolio
    result = []
    for portfolio in portfolios:
        portfolio_dict = portfolio.dict()
        
        # Calculate portfolio totals
        total_value = 0
        total_cost = 0
        
        for holding in portfolio.holdings:
            # Get current price (mock for now, will add real API later)
            current_price = await get_current_price(holding.symbol)
            holding_value = holding.shares * current_price
            holding_cost = holding.shares * holding.purchase_price
            
            total_value += holding_value
            total_cost += holding_cost
        
        portfolio_dict["total_value"] = total_value
        portfolio_dict["total_cost"] = total_cost
        portfolio_dict["total_gain_loss"] = total_value - total_cost
        if total_cost > 0:
            portfolio_dict["total_gain_loss_percentage"] = ((total_value - total_cost) / total_cost) * 100
        else:
            portfolio_dict["total_gain_loss_percentage"] = 0
            
        result.append(portfolio_dict)
    
    return result

@router.get("/{portfolio_id}", response_model=PortfolioOut)
async def get_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific portfolio by ID
    """
    portfolio = await Portfolio.get(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    if portfolio.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this portfolio"
        )
    
    # Calculate totals
    total_value = 0
    total_cost = 0
    
    for holding in portfolio.holdings:
        current_price = await get_current_price(holding.symbol)
        holding_value = holding.shares * current_price
        holding_cost = holding.shares * holding.purchase_price
        
        total_value += holding_value
        total_cost += holding_cost
    
    portfolio_dict = portfolio.dict()
    portfolio_dict["total_value"] = total_value
    portfolio_dict["total_cost"] = total_cost
    portfolio_dict["total_gain_loss"] = total_value - total_cost
    if total_cost > 0:
        portfolio_dict["total_gain_loss_percentage"] = ((total_value - total_cost) / total_cost) * 100
    else:
        portfolio_dict["total_gain_loss_percentage"] = 0
    
    return portfolio_dict

@router.post("/{portfolio_id}/holdings", response_model=PortfolioOut)
async def add_holding(
    portfolio_id: str,
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add a holding to a portfolio
    """
    portfolio = await Portfolio.get(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    if portfolio.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this portfolio"
        )
    
    # Add holding
    portfolio.holdings.append(holding_data)
    portfolio.updated_at = datetime.utcnow()
    
    await portfolio.save()
    return portfolio

@router.delete("/{portfolio_id}/holdings/{holding_index}")
async def remove_holding(
    portfolio_id: str,
    holding_index: int,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a holding from a portfolio
    """
    portfolio = await Portfolio.get(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    if portfolio.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this portfolio"
        )
    
    if holding_index < 0 or holding_index >= len(portfolio.holdings):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid holding index"
        )
    
    # Remove holding
    portfolio.holdings.pop(holding_index)
    portfolio.updated_at = datetime.utcnow()
    
    await portfolio.save()
    
    return {"message": "Holding removed successfully"}

@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a portfolio
    """
    portfolio = await Portfolio.get(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    if portfolio.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this portfolio"
        )
    
    await portfolio.delete()
    
    return {"message": "Portfolio deleted successfully"}