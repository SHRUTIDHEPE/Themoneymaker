import asyncio
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_beanie():
    """Test Beanie initialization"""
    from database.mongodb import connect_to_mongodb, close_mongodb_connection
    from models.mongo_models import User
    
    print("🔍 Testing Beanie initialization...")
    
    # Connect to MongoDB
    success = await connect_to_mongodb()
    if not success:
        print("❌ Failed to connect to MongoDB")
        return
    
    try:
        # Try to find a user (should work if Beanie is initialized)
        print("Testing User collection...")
        users = await User.find_all().to_list()
        print(f"✅ User.find_all() worked! Found {len(users)} users")
        
        print("✅ Beanie is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongodb_connection()

if __name__ == "__main__":
    asyncio.run(test_beanie())