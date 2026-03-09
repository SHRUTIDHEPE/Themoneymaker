import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

load_dotenv()

async def test_connection():
    """Simple test for MongoDB connection"""
    print(" Testing MongoDB Connection...")
    
    # Get connection string
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "moneymaker")
    
    print(f" Database: {db_name}")
    print(f"Connecting to: {mongo_url[:30]}..." if len(mongo_url) > 30 else f"🔌 Connecting to: {mongo_url}")
    
    try:
        # Connect
        client = AsyncIOMotorClient(mongo_url)
        
        # Ping
        await client.admin.command('ping')
        print("MongoDB server is reachable")
        
        # Get database
        db = client[db_name]
        
        # List collections
        collections = await db.list_collection_names()
        print(f" Existing collections: {collections if collections else 'None'}")
        
        # Create a test collection and insert a document
        test_collection = db.test_connection
        result = await test_collection.insert_one({
            "test": "connection successful",
            "timestamp": datetime.utcnow()
        })
        print(f"Test document inserted with ID: {result.inserted_id}")
        
        # Clean up
        await test_collection.delete_one({"_id": result.inserted_id})
        print("Test document cleaned up")
        
        client.close()
        print("All tests passed! MongoDB is ready to use.")
        return True
        
    except Exception as e:
        print(f" Connection failed: {e}")
        print("\n Troubleshooting tips:")
        print("  - If using local MongoDB: Make sure MongoDB service is running")
        print("  - Run: Get-Service MongoDB (check if status is 'Running')")
        print("  - If using Atlas: Check username/password in connection string")
        print("  - Check network/firewall settings")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())