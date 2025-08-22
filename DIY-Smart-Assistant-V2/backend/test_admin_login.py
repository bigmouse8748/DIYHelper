#!/usr/bin/env python3
"""
Test admin login
"""

import requests
import json

def test_admin_login():
    """Test admin login via API"""
    url = "http://localhost:8000/api/v1/auth/login"
    
    login_data = {
        "email": "admin@diyassistant.com", 
        "password": "DIYAdmin2025!"
    }
    
    try:
        response = requests.post(url, json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("Admin login successful!")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Username: {data.get('user', {}).get('username')}")
            print(f"User Type: {data.get('user', {}).get('user_type')}")
            print(f"Access Token: {data.get('access_token', '')[:50]}...")
        else:
            print("Admin login failed!")
            
    except Exception as e:
        print(f"Error testing login: {e}")

if __name__ == "__main__":
    test_admin_login()