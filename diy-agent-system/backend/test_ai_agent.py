#!/usr/bin/env python3
"""
Test script for ProductInfoAgent with various affiliate links
"""
import asyncio
import logging
from agents.product_info_agent import ProductInfoAgent
from core.agent_base import AgentTask
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_product_info_agent():
    """Test the ProductInfoAgent with various affiliate links"""
    
    # Initialize agent
    agent = ProductInfoAgent()
    
    # Test URLs with affiliate links (these would be real affiliate links in production)
    test_urls = [
        # Amazon product with affiliate parameters
        "https://www.amazon.com/DEWALT-DCD771C2-Cordless-Lithium-Ion-Compact/dp/B00ET5VMTU?tag=diyhelper-20&linkCode=ogi&th=1",
        
        # Home Depot product link
        "https://www.homedepot.com/p/Milwaukee-M18-FUEL-18-Volt-Lithium-Ion-Brushless-Cordless-7-1-4-in-Circular-Saw-Tool-Only-2730-20/206497461",
        
        # Lowes product link
        "https://www.lowes.com/pd/CRAFTSMAN-V20-20-Volt-Max-1-2-in-Cordless-Drill-1-Battery-Included/1000578031",
        
        # Walmart product link
        "https://www.walmart.com/ip/HART-20-Volt-Cordless-1-2-inch-Drill-Driver-Kit-with-1-5Ah-Lithium-Ion-Battery-and-Charger/55851909"
    ]
    
    print("=== Testing ProductInfoAgent with Affiliate Links ===\n")
    
    for i, url in enumerate(test_urls, 1):
        print(f"[Test {i}] {url}")
        print("-" * 80)
        
        try:
            # Create agent task
            task = AgentTask(
                task_id=f"test_product_{i}_{datetime.utcnow().timestamp()}",
                agent_name="product_info_extraction",
                input_data={
                    "product_url": url
                },
                created_at=datetime.utcnow()
            )
            
            # Execute agent
            result = await agent.process_task(task)
            
            if result.success:
                data = result.data
                print(f"[SUCCESS] Extraction Method: {data.get('extraction_method', 'unknown')}")
                print(f"   Title: {data.get('title', 'N/A')}")
                print(f"   Merchant: {data.get('merchant', 'N/A')}")
                print(f"   URL Preserved: {data.get('product_url') == url}")
                print(f"   Price: ${data.get('sale_price', data.get('original_price', 'N/A'))}")
                print(f"   Brand: {data.get('brand', 'N/A')}")
                print(f"   Category: {data.get('category', 'N/A')}")
                print(f"   Rating: {data.get('rating', 'N/A')}")
                
                # Verify affiliate link preservation
                if data.get('product_url') == url:
                    print("   [OK] Affiliate link preserved correctly")
                else:
                    print("   [WARNING] Affiliate link may have been modified")
                    print(f"      Original: {url}")
                    print(f"      Returned: {data.get('product_url')}")
                    
            else:
                print(f"[FAILED] {result.error}")
                
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            
        print("\n")
    
    print("=== Test Summary ===")
    print("[COMPLETED] ProductInfoAgent testing completed")
    print("[INFO] All affiliate links should be preserved exactly as provided")
    print("[INFO] AI extraction provides better product information than web scraping")

if __name__ == "__main__":
    asyncio.run(test_product_info_agent())