from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
import logging

# Import your models
from models.mongo_models import User, Portfolio, StockPrice, Alert

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None
    is_connected: bool = False

db = Database()

async def connect_to_mongodb():
    try:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "moneymaker")

        logger.info(f"Connecting to MongoDB: {db_name}")
        logger.info(f"Connection URL: {mongo_url}")

        # Base options (no SSL by default)
        client_options = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 5000,
        }

        # For localhost, we explicitly do NOT use SSL
        if "localhost" in mongo_url or "127.0.0.1" in mongo_url:
            logger.info("Detected local MongoDB – disabling SSL")
            client_options["tls"] = False
            client_options["ssl"] = False
        else:
            # For remote (Atlas) you can add SSL options if needed later
            client_options["tls"] = True

        db.client = AsyncIOMotorClient(mongo_url, **client_options)

        # Ping to verify connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB ping successful")

        db.database = db.client[db_name]

        # Initialize Beanie
        await init_beanie(
            database=db.database,
            document_models=[User, Portfolio, StockPrice, Alert]
        )
        logger.info("✅ Beanie initialized")

        db.is_connected = True
        logger.info(f"✅ Connected to MongoDB: {db_name}")

        # Show existing collections (optional)
        collections = await db.database.list_collection_names()
        logger.info(f"📚 Collections: {collections}")

        return True

    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        db.is_connected = False
        return False

async def close_mongodb_connection():
    if db.client:
        db.client.close()
        db.is_connected = False
        logger.info("✅ MongoDB connection closed")

async def get_database():
    return db.database