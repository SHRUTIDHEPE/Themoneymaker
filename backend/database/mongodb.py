from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
import logging
import certifi
import ssl

# Import your models
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
        
        # For Windows SSL issues, try these connection options
        client_options = {
            "serverSelectionTimeoutMS": 30000,  # 30 seconds
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000,
            "tls": True,
            "tlsAllowInvalidCertificates": True,  # For development only
            "retryWrites": True,
        }
        
        # For Atlas, you might need this
        if "mongodb+srv" in mongo_url:
            client_options["tlsCAFile"] = certifi.where()
        
        # Create Motor client with options
        db.client = AsyncIOMotorClient(mongo_url, **client_options)
        
        # Ping the database to verify connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB ping successful")
        
        # Get database
        db.database = db.client[db_name]
        
        # Initialize Beanie ODM
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
        logger.error("💡 Troubleshooting tips:")
        logger.error("  1. Check if your IP is whitelisted in MongoDB Atlas")
        logger.error("  2. Verify username/password in connection string")
        logger.error("  3. Try adding '&ssl=true&tlsAllowInvalidCertificates=true' to URL")
        logger.error("  4. Install certifi: pip install certifi")
        logger.error("  5. Temporarily use local MongoDB for development")
        return False

async def close_mongodb_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")

# Dependency to get database
async def get_database():
    return db.database