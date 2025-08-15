"""
Test improved Amazon price extraction
"""
import asyncio
from agents.product_info_agent import ProductInfoAgent

async def test_amazon_price():
    agent = ProductInfoAgent()
    
    # Test various Amazon URLs
    test_urls = [
        ('https://amzn.to/470G49y', 'Amazon short link'),
        ('https://www.amazon.com/dp/B00NMSQZGE', 'Amazon direct product'),
        ('https://www.amazon.com/DEWALT-Cordless-Drill-Combo-DCK240C2/dp/B00IJ0ALYS', 'DeWalt drill'),
    ]
    
    for url, description in test_urls:
        print(f'\nTesting {description}...')
        print(f'URL: {url}')
        
        result = await agent.execute({'product_url': url})
        
        if result.success:
            data = result.data
            print(f'  Title: {data.get("title")}')
            print(f'  Category: {data.get("category")}')
            print(f'  Price: ${data.get("sale_price", "None")}')
            print(f'  Method: {data.get("extraction_method")}')
            
            if data.get("sale_price"):
                print(f'  >>> SUCCESS: Price found!')
            else:
                print(f'  >>> WARNING: No price found')
        else:
            print(f'  Error: {result.error}')
        
        print('-' * 50)

if __name__ == "__main__":
    asyncio.run(test_amazon_price())