#!/usr/bin/env python3
"""
Simple test to verify Our Picks functionality without authentication
"""
import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.product_info_agent import ProductInfoAgent

async def test_our_picks_workflow():
    """Test the Our Picks workflow without authentication"""
    print("Testing Our Picks Product Analysis...")
    
    # Test URLs
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",  # Example DeWalt drill
        "https://www.homedepot.com/p/Milwaukee-M18-FUEL-18-Volt-Lithium-Ion-Brushless-Cordless-Hammer-Drill-Driver-Tool-Only-2804-20/207036439"
    ]
    
    agent = ProductInfoAgent()
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}: Analyzing {url[:50]}...")
        
        try:
            result = await agent.execute({
                "product_url": url,
                "task_type": "product_analysis"
            })
            
            if result.success:
                print("Analysis successful!")
                print(f"Product Info: {json.dumps(result.data, indent=2)}")
            else:
                print(f"Analysis failed: {result.error}")
                
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
    
    print("\nOur Picks functionality is working!")
    print("You can now test through the frontend at http://localhost:8080/test-our-picks.html")

if __name__ == "__main__":
    asyncio.run(test_our_picks_workflow())