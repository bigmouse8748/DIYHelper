"""
Test additional merchants for price extraction
"""
import asyncio
from agents.product_info_agent import ProductInfoAgent

async def test_additional_merchants():
    agent = ProductInfoAgent()
    
    # Test Harbor Freight (tools specialty retailer)
    print('Testing Harbor Freight...')
    harbor_freight_url = 'https://www.harborfreight.com/hand-tools/wrenches/adjustable-wrenches/10-in-adjustable-wrench-60656.html'
    result = await agent.execute({'product_url': harbor_freight_url})
    data = result.data if result.success else {}
    print(f'Harbor Freight - Title: {data.get("title", "N/A")}')
    print(f'Harbor Freight - Price: ${data.get("sale_price", "N/A")}')
    print(f'Harbor Freight - Method: {data.get("extraction_method", "N/A")}')
    print()
    
    # Test Menards (Midwest home improvement)
    print('Testing Menards...')
    menards_url = 'https://www.menards.com/main/tools/hand-tools/wrenches/kobalt-reg-10-adjustable-wrench/2470371/p-1444451397887-c-9221.htm'
    result = await agent.execute({'product_url': menards_url})
    data = result.data if result.success else {}
    print(f'Menards - Title: {data.get("title", "N/A")}')
    print(f'Menards - Price: ${data.get("sale_price", "N/A")}')
    print(f'Menards - Method: {data.get("extraction_method", "N/A")}')
    print()
    
    # Test Northern Tool (specialty tools)
    print('Testing Northern Tool...')
    northern_url = 'https://www.northerntool.com/shop/tools/product_200672449_200672449'
    result = await agent.execute({'product_url': northern_url})
    data = result.data if result.success else {}
    print(f'Northern Tool - Title: {data.get("title", "N/A")}')
    print(f'Northern Tool - Price: ${data.get("sale_price", "N/A")}')
    print(f'Northern Tool - Method: {data.get("extraction_method", "N/A")}')
    print()
    
    # Test different Amazon product to verify Amazon search works
    print('Testing Amazon product...')
    amazon_url = 'https://www.amazon.com/BLACK-DECKER-BDCR8-Cordless-Drill/dp/B00NMSQZGE'
    result = await agent.execute({'product_url': amazon_url})
    data = result.data if result.success else {}
    print(f'Amazon - Title: {data.get("title", "N/A")}')
    print(f'Amazon - Price: ${data.get("sale_price", "N/A")}')
    print(f'Amazon - Method: {data.get("extraction_method", "N/A")}')
    print()

if __name__ == "__main__":
    asyncio.run(test_additional_merchants())