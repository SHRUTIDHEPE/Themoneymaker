import random
from typing import Optional

# Mock stock prices for testing
MOCK_PRICES = {
    "AAPL": 175.50,
    "MSFT": 380.25,
    "GOOGL": 140.30,
    "AMZN": 145.75,
    "TSLA": 240.15,
    "META": 320.40,
    "NVDA": 850.20,
    "JPM": 155.80,
    "V": 250.60,
    "WMT": 165.30,
}

async def get_current_price(symbol: str) -> float:
    """
    Get current stock price
    For now, returns mock data. Will integrate with real API later.
    """
    symbol = symbol.upper()
    
    # Return mock price if available
    if symbol in MOCK_PRICES:
        # Add small random variation
        base_price = MOCK_PRICES[symbol]
        variation = random.uniform(-2, 2)
        return round(base_price + variation, 2)
    
    # Default mock price for unknown symbols
    return round(random.uniform(50, 500), 2)

async def search_stocks(query: str) -> list:
    """
    Search for stocks by symbol or name
    Mock implementation
    """
    results = []
    for symbol in MOCK_PRICES.keys():
        if query.upper() in symbol:
            results.append({
                "symbol": symbol,
                "name": f"{symbol} Inc.",  # Mock company name
                "price": MOCK_PRICES[symbol]
            })
    
    return results[:5]  # Return top 5 matches