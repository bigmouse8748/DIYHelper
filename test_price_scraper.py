#!/usr/bin/env python3
"""
测试价格抓取服务
"""
import asyncio
import sys
import os

# 添加backend路径到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'diy-agent-system', 'backend'))

from services.price_scraper import get_product_prices

async def test_price_scraping():
    """测试真实价格抓取"""
    
    print("Price Scraping Service Test")
    print("=" * 40)
    
    test_cases = [
        {
            "brand": "DeWalt",
            "model": "DCD771C2", 
            "tool": "Drill",
            "description": "DeWalt 20V Drill"
        },
        {
            "brand": "Milwaukee",
            "model": "2630-20",
            "tool": "Circular Saw", 
            "description": "Milwaukee Circular Saw"
        },
        {
            "brand": "DeWalt", 
            "model": "DWE7491RS",
            "tool": "Table Saw",
            "description": "DeWalt Table Saw"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test['description']} ---")
        print(f"Query: {test['brand']} {test['model']} {test['tool']}")
        
        try:
            results = await get_product_prices(
                test["brand"], 
                test["model"], 
                test["tool"]
            )
            
            if results:
                print(f"[SUCCESS] Found {len(results)} price results:")
                for j, product in enumerate(results, 1):
                    print(f"  {j}. {product.retailer}")
                    print(f"     Title: {product.title}")
                    print(f"     Price: ${product.price:.2f}")
                    print(f"     In Stock: {product.in_stock}")
                    print(f"     URL: {product.url[:60]}...")
                    if product.rating > 0:
                        print(f"     Rating: {product.rating:.1f} ({product.review_count} reviews)")
                    print()
            else:
                print("[WARNING] No prices found")
                
        except Exception as e:
            print(f"[ERROR] Price scraping failed: {str(e)}")
    
    print("\nPrice scraping test completed!")

if __name__ == "__main__":
    asyncio.run(test_price_scraping())