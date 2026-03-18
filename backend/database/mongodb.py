from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
import logging
import certifi
import asyncio

# Import your models
from models.mongo_models import User, Portfolio, StockPrice, Alert

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None
    is_connected: bool = False

db = Database()

async def connect_to_mongodb():
    """Initialize MongoDB connection with proper SSL"""
    try:
        # Get connection string from .env
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "moneymaker")
        
        # Mask password for logging
        masked_url = mongo_url
        if '@' in mongo_url:
            parts = mongo_url.split('@')
            credentials = parts[0].split('://')[1].split(':')
            if len(credentials) > 1:
                masked_url = mongo_url.replace(credentials[1], '****')
        
        logger.info(f"Connecting to MongoDB: {db_name}")
        logger.info(f"Connection URL: {masked_url}")
        
        # Connection options
        client_options = {
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000,
            "tls": True,
            "tlsAllowInvalidCertificates": True,
            "retryWrites": True,
        }
        
        # For Atlas, add CA file
        if "mongodb+srv" in mongo_url:
            client_options["tlsCAFile"] = certifi.where()
        
        # Create Motor client with options
        db.client = AsyncIOMotorClient(mongo_url, **client_options)
        
        # Ping the database to verify connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB ping successful")
        
        # Get database
        db.database = db.client[db_name]
        
        # IMPORTANT: Initialize Beanie with ALL document models
        logger.info("Initializing Beanie with document models...")
        await init_beanie(
            database=db.database,
            document_models=[
                User,        # User model
                Portfolio,   # Portfolio model
                StockPrice,  # StockPrice model
                Alert        # Alert model
            ]
        )
        logger.info("✅ Beanie initialized successfully")
        
        db.is_connected = True
        logger.info(f"✅ Connected to MongoDB: {db_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.is_connected = False
        return False

async def close_mongodb_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        db.is_connected = False
        logger.info("✅ MongoDB connection closed")

# Dependency to get database
async def get_database():
    return db.database