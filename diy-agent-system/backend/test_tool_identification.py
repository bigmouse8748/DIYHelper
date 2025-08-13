"""
Test script for Tool Identification API
"""
import requests
import base64
import json
import sys
from pathlib import Path

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
API_BASE = "http://localhost:8002"
DEMO_TOKEN = None

def login():
    """Login with demo user and get token"""
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        data={"username": "demo", "password": "demo123"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful! User: {data['user_info']['username']}")
        print(f"   Membership: {data['user_info']['membership_level']}")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_tool_identification(token, image_path=None):
    """Test tool identification with a mock image"""
    
    # Create a mock image if not provided
    if image_path is None:
        # Create a simple 1x1 pixel image as base64
        mock_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xa5\xac\xc4J\x00\x00\x00\x00IEND\xaeB`\x82'
    else:
        with open(image_path, 'rb') as f:
            mock_image = f.read()
    
    # Prepare the request
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        'image': ('tool.png', mock_image, 'image/png')
    }
    
    data = {
        'include_alternatives': True
    }
    
    print("\n📸 Sending tool image for identification...")
    
    response = requests.post(
        f"{API_BASE}/api/identify-tool",
        headers=headers,
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Tool Identification Successful!")
        print(f"\n🔧 Tool Information:")
        tool_info = result['tool_info']
        print(f"   Name: {tool_info['name']}")
        print(f"   Brand: {tool_info['brand']}")
        print(f"   Model: {tool_info['model']}")
        print(f"   Category: {tool_info['category']}")
        print(f"   Confidence: {tool_info['confidence']:.2%}")
        
        if tool_info.get('specifications'):
            print(f"\n📋 Specifications:")
            for key, value in tool_info['specifications'].items():
                print(f"   - {key}: {value}")
        
        print(f"\n🛒 Exact Matches ({len(result['exact_matches'])} found):")
        for match in result['exact_matches'][:3]:
            print(f"   📍 {match['retailer'].upper()}")
            print(f"      Title: {match['title']}")
            print(f"      Price: ${match['price']}")
            print(f"      URL: {match['url']}")
            print(f"      In Stock: {'✅' if match['in_stock'] else '❌'}")
        
        print(f"\n🔄 Alternative Products ({len(result['alternatives'])} found):")
        for alt in result['alternatives'][:3]:
            print(f"   📍 {alt['retailer'].upper()}")
            print(f"      Title: {alt['title']}")
            print(f"      Price: ${alt['price']}")
        
        print(f"\n📊 User Quota:")
        quota = result['user_quota']
        print(f"   Used: {quota['used']}/{quota['limit']}")
        print(f"   Membership: {quota['membership']}")
        
    elif response.status_code == 429:
        print(f"❌ Daily limit reached! {response.json()['detail']}")
    else:
        print(f"❌ Tool identification failed: {response.text}")

def test_history(token):
    """Test getting identification history"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{API_BASE}/api/identification-history",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📜 Identification History:")
        print(f"   Total records: {data['total']}")
        print(f"   Membership: {data['membership']}")
        
        if data['history']:
            print(f"\n   Recent identifications:")
            for item in data['history'][:3]:
                print(f"   - {item['tool_info']['name']} ({item['tool_info']['brand']} {item['tool_info']['model']})")
                print(f"     Identified at: {item['search_timestamp']}")
    else:
        print(f"❌ Failed to get history: {response.text}")

def test_user_info(token):
    """Test getting current user info"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{API_BASE}/api/auth/me",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n👤 Current User Info:")
        print(f"   Username: {data['username']}")
        print(f"   Email: {data['email']}")
        print(f"   Membership: {data['membership_level']}")
        print(f"   Daily Usage: {data['daily_identifications']}/{data['daily_limit']}")
    else:
        print(f"❌ Failed to get user info: {response.text}")

def main():
    print("=" * 60)
    print("🔧 Tool Identification API Test Suite")
    print("=" * 60)
    
    # Step 1: Login
    token = login()
    if not token:
        return
    
    # Step 2: Get user info
    test_user_info(token)
    
    # Step 3: Test tool identification
    test_tool_identification(token)
    
    # Step 4: Check history
    test_history(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()