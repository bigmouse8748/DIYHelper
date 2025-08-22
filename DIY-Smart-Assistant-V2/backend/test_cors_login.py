#!/usr/bin/env python3
"""
Test admin login with CORS headers
"""

import requests
import json

def test_cors_login():
    """Test admin login via API with CORS headers"""
    url = "http://localhost:8000/api/v1/auth/login"
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:8080"
    }
    
    login_data = {
        "email": "admin@diyassistant.com", 
        "password": "DIYAdmin2025!"
    }
    
    try:
        # Test preflight first
        print("Testing CORS preflight...")
        preflight_headers = {
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        preflight_response = requests.options(url, headers=preflight_headers)
        print(f"Preflight Status: {preflight_response.status_code}")
        print(f"Preflight Headers: {dict(preflight_response.headers)}")
        
        # Test actual request
        print("\nTesting actual login...")
        response = requests.post(url, json=login_data, headers=headers)
        
        print(f"Login Status Code: {response.status_code}")
        print(f"Login Response Headers: {dict(response.headers)}")
        print(f"Login Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Login successful!")
            print(f"User Type: {data.get('user', {}).get('user_type')}")
        else:
            print("\n❌ Login failed!")
            
    except Exception as e:
        print(f"Error testing login: {e}")

if __name__ == "__main__":
    test_cors_login()