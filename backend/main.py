from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from database.mongodb import connect_to_mongodb, close_mongodb_connection, db
from routes.auth import router as auth_router  # Changed this line

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
app.include_router(auth_router)  # Updated this line

@app.get("/")
async def root():
    return {
        "message": "💰 Money Maker API",
        "version": "1.0.0",
        "database": "connected" if db.database else "disconnected",
        "endpoints": {
            "docs": "/docs",
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            }
        }
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