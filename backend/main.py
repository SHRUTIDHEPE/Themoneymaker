from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from database.mongodb import connect_to_mongodb, close_mongodb_connection, db  # Make sure db is imported
from routes.auth import router as auth_router
from routes.portfolio import router as portfolio_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    print("🚀 Starting Money Maker API...")
    success = await connect_to_mongodb()
    if not success:
        print("⚠️  WARNING: MongoDB connection failed. Check your .env file and MongoDB server.")
    yield
    # Shutdown: Close connection
    await close_mongodb_connection()
    print("👋 Money Maker API shutdown complete")

app = FastAPI(
    title="Money Maker API",
    description="Financial Dashboard with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(portfolio_router)

@app.get("/")
async def root():
    # Use the is_connected flag instead of checking db.database directly
    return {
        "message": "💰 Money Maker API",
        "version": "1.0.0",
        "database": "connected" if db.is_connected else "disconnected",
        "endpoints": {
            "docs": "/docs",
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            },
            "portfolios": {
                "create": "POST /portfolios",
                "list": "GET /portfolios",
                "get": "GET /portfolios/{id}",
                "add_holding": "POST /portfolios/{id}/holdings"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies MongoDB connection"""
    try:
        # Try to ping MongoDB
        if db.client is not None:
            await db.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    return {
        "status": "degraded",
        "database": "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }