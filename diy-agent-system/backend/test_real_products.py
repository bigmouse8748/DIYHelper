"""
Test real current product URLs
"""
import asyncio
from agents.product_info_agent import ProductInfoAgent

async def test_real_products():
    agent = ProductInfoAgent()
    
    # Real current Amazon drill
    print('Testing real Amazon drill...')
    amazon_url = 'https://www.amazon.com/dp/B00NMSQZGE'
    result = await agent.execute({'product_url': amazon_url})
    data = result.data if result.success else {}
    print(f'Amazon - Title: {data.get("title", "N/A")}')
    print(f'Amazon - Price: ${data.get("sale_price", "N/A")}')
    print(f'Amazon - Method: {data.get("extraction_method", "N/A")}')
    print()
    
    # Real current Home Depot product
    print('Testing real Home Depot product...')
    homedepot_url = 'https://www.homedepot.com/p/RYOBI-ONE-HP-18V-Brushless-Cordless-1-2-in-Drill-Driver-with-1-5-Ah-Battery-and-Charger-Kit-PSBDD01K/308503371'
    result = await agent.execute({'product_url': homedepot_url})
    data = result.data if result.success else {}
    print(f'Home Depot - Title: {data.get("title", "N/A")}')
    print(f'Home Depot - Price: ${data.get("sale_price", "N/A")}')
    print(f'Home Depot - Method: {data.get("extraction_method", "N/A")}')
    print()
    
    # Real current Lowes product
    print('Testing real Lowes product...')
    lowes_url = 'https://www.lowes.com/pd/CRAFTSMAN-V20-20-Volt-Max-1-2-in-Cordless-Drill-1-Battery-Included/1000595607'
    result = await agent.execute({'product_url': lowes_url})
    data = result.data if result.success else {}
    print(f'Lowes - Title: {data.get("title", "N/A")}')
    print(f'Lowes - Price: ${data.get("sale_price", "N/A")}')
    print(f'Lowes - Method: {data.get("extraction_method", "N/A")}')
    print()

if __name__ == "__main__":
    asyncio.run(test_real_products())