import asyncio
import httpx
import json

async def test_register():
    """Test registration directly with HTTP"""
    url = "http://localhost:8000/auth/register"
    data = {
        "email": "direct_test@example.com",
        "password": "password123"
    }
    
    print(f"Sending POST to {url}")
    print(f"Data: {data}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Registration successful!")
            else:
                print(f"❌ Registration failed: {response.text}")
        except Exception as e:
            print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_register())