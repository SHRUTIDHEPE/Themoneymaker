from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
import logging

# Import your models (we'll create these next)
from models.mongo_models import User, Portfolio, StockPrice, Alert

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongodb():
    """Initialize MongoDB connection"""
    try:
        # Get connection string from .env
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "moneymaker")
        
        logger.info(f"Connecting to MongoDB: {db_name}")
        
        # Create Motor client
        db.client = AsyncIOMotorClient(mongo_url)
        
        # Ping the database to verify connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB ping successful")
        
        # Get database
        db.database = db.client[db_name]
        
        # Initialize Beanie ODM with all document models
        await init_beanie(
            database=db.database,
            document_models=[
                User,
                Portfolio, 
                StockPrice,
                Alert
            ]
        )
        
        logger.info(f"✅ Connected to MongoDB: {db_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

async def close_mongodb_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")

# Dependency to get database
async def get_database():
    return db.database