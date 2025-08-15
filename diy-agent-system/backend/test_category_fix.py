"""
Test category validation fix
"""
import asyncio
from agents.product_info_agent import ProductInfoAgent

async def test_category_fix():
    agent = ProductInfoAgent()
    
    # Test with an Amazon automotive product that was failing
    print('Testing Amazon automotive product...')
    amazon_url = 'https://amzn.to/470G49y'
    result = await agent.execute({'product_url': amazon_url})
    
    if result.success:
        data = result.data
        print(f'Title: {data.get("title")}')
        print(f'Category: {data.get("category")}')  # Should be 'tools' not 'automotive'
        print(f'Price: ${data.get("sale_price")}')
        print(f'Extraction method: {data.get("extraction_method")}')
        print('\nSuccess! Category is now valid:', data.get("category") in ['tools', 'materials', 'safety', 'accessories', 'other'])
    else:
        print(f'Error: {result.error}')

if __name__ == "__main__":
    asyncio.run(test_category_fix())