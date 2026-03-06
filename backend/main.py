from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from database.mongodb import connect_to_mongodb, close_mongodb_connection

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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "💰 Money Maker API",
        "database": "MongoDB",
        "status": "connected" if db.database else "disconnected"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies MongoDB connection"""
    try:
        # Try to ping MongoDB
        if db.client:
            await db.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
    except:
        pass
    
    return {
        "status": "degraded",
        "database": "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

# Import db from mongodb for endpoints
from database.mongodb import db