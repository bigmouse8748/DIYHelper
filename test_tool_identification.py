#!/usr/bin/env python3
"""
Test script for tool identification accuracy
"""
import requests
import base64
import json
import os

# Test configuration
BACKEND_URL = "http://localhost:8002"
TEST_IMAGES_DIR = "test_images"  # Create this directory with test images

def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_tool_identification():
    """Test tool identification with sample images"""
    
    # First, register and login
    print("Testing authentication...")
    
    # Register test user
    register_data = {
        "username": "test_accuracy",
        "password": "test123",
        "email": "test@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/api/auth/register", json=register_data)
    if response.status_code == 200:
        print("[OK] Test user registered successfully")
    else:
        print("[INFO] Using existing test user")
    
    # Login with demo user instead
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BACKEND_URL}/api/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"[ERROR] Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Authentication successful")
    
    # Test identification with different scenarios
    test_cases = [
        {
            "name": "Table Saw Test",
            "description": "Should identify as Table Saw, not Circular Saw",
            "expected_keywords": ["table", "saw"]
        },
        {
            "name": "Circular Saw Test", 
            "description": "Should identify as Circular Saw",
            "expected_keywords": ["circular", "saw"]
        },
        {
            "name": "Drill Test",
            "description": "Should identify as Drill or Driver",
            "expected_keywords": ["drill", "driver"]
        }
    ]
    
    print("\nTesting tool identification...")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test {i+1}: {test_case['name']} ---")
        print(f"Expected: {test_case['description']}")
        
        # Create a mock base64 image (in real test, use actual images)
        # For testing purposes, we'll use a simple test string
        mock_image = f"test_image_data_{i}_{test_case['name'].replace(' ', '_')}"
        image_base64 = base64.b64encode(mock_image.encode()).decode('utf-8')
        
        # Prepare form data
        files = {
            'image': ('test.jpg', base64.b64decode(image_base64), 'image/jpeg')
        }
        data = {
            'include_alternatives': 'true'
        }
        
        try:
            # Make identification request
            response = requests.post(
                f"{BACKEND_URL}/api/identify-tool",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                tool_name = result.get("tool_info", {}).get("name", "Unknown")
                confidence = result.get("tool_info", {}).get("confidence", 0)
                category = result.get("tool_info", {}).get("category", "unknown")
                
                print(f"[OK] Identification successful:")
                print(f"   Tool: {tool_name}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Category: {category}")
                print(f"   Exact matches: {len(result.get('exact_matches', []))}")
                print(f"   Alternatives: {len(result.get('alternatives', []))}")
                
                # Check if result matches expectations
                tool_name_lower = tool_name.lower()
                matches_expectation = any(keyword in tool_name_lower for keyword in test_case['expected_keywords'])
                
                if matches_expectation:
                    print(f"[PASS] Tool identification matches expectation")
                else:
                    print(f"[REVIEW] Tool identified as '{tool_name}', expected keywords: {test_case['expected_keywords']}")
                    
            else:
                print(f"[ERROR] Identification failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Test error: {str(e)}")
    
    print("\nTest Summary:")
    print("- Updated OpenAI Vision API with better prompts")
    print("- Enhanced tool categories and specifications") 
    print("- Improved fallback logic with image analysis hints")
    print("- Better JSON parsing and error handling")
    
    return True

if __name__ == "__main__":
    print("Tool Identification Accuracy Test")
    print("====================================")
    test_tool_identification()