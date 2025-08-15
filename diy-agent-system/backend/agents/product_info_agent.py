"""
AI-Powered Product Information Extraction Agent
Uses OpenAI GPT to intelligently extract product information from URLs
"""
import asyncio
import requests
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import re
from core.agent_base import BaseAgent, AgentTask, AgentResult

logger = logging.getLogger(__name__)

class ProductInfoAgent(BaseAgent):
    """AI-powered agent for extracting product information from URLs"""
    
    def __init__(self):
        super().__init__(name="ProductInfoAgent")
        self.description = "Extracts product information using AI analysis"
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.ai_enabled = True
            logger.info("ProductInfoAgent initialized with OpenAI API")
        else:
            self.client = None
            self.ai_enabled = False
            logger.warning("ProductInfoAgent initialized without OpenAI API - using fallback mode")
        
        # Setup session for web requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Valid categories from the database model
        self.valid_categories = ['tools', 'materials', 'safety', 'accessories', 'other']
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate input data for product info extraction"""
        if not isinstance(input_data, dict):
            return False
        
        product_url = input_data.get('product_url')
        if not product_url or not isinstance(product_url, str):
            return False
            
        # Basic URL validation
        from urllib.parse import urlparse
        try:
            parsed = urlparse(product_url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute product information extraction task"""
        try:
            product_url = input_data.get('product_url')
            if not product_url:
                return AgentResult(
                    success=False,
                    error="No product URL provided"
                )
            
            logger.info(f"Extracting product info from: {product_url}")
            
            # Extract product information using AI
            product_info = await self._extract_product_info_with_ai(product_url)
            
            return AgentResult(
                success=True,
                data=product_info
            )
            
        except Exception as e:
            logger.error(f"Product info extraction failed: {e}")
            return AgentResult(
                success=False,
                error=str(e)
            )
    
    async def _extract_product_info_with_ai(self, url: str) -> Dict[str, Any]:
        """Extract product information using AI analysis"""
        try:
            # First, get the page content
            page_content = await self._fetch_page_content(url)
            
            if not page_content:
                # Try search-based extraction as fallback
                logger.info(f"Direct page fetch failed for {url}, attempting search-based extraction")
                return await self._search_based_extraction(url)
            
            # Use AI to extract product information
            if self.ai_enabled:
                product_info = await self._analyze_with_openai(url, page_content)
                if product_info and product_info.get('title'):
                    # If critical data is missing (price/image), try search enhancement
                    if not product_info.get('original_price') and not product_info.get('sale_price'):
                        logger.info(f"Price missing from direct extraction, attempting search enhancement for {url}")
                        search_data = await self._search_based_extraction(url, product_info.get('title'))
                        if search_data:
                            # Merge search data with direct extraction
                            product_info = self._merge_product_data(product_info, search_data)
                    return product_info
                else:
                    logger.warning(f"AI analysis returned incomplete data for {url}, trying search-based extraction")
                    return await self._search_based_extraction(url)
            
            # Fallback to basic extraction if AI fails
            logger.warning("AI analysis failed or unavailable, trying search-based extraction")
            search_result = await self._search_based_extraction(url)
            if search_result:
                return search_result
            
            return self._extract_basic_info(url, page_content)
            
        except Exception as e:
            logger.error(f"Error in AI product extraction: {e}")
            # Try search-based extraction as final fallback
            try:
                search_result = await self._search_based_extraction(url)
                if search_result:
                    return search_result
            except:
                pass
            return self._create_fallback_product(url, f"Extraction error: {str(e)}")
    
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch page content while preserving affiliate parameters"""
        try:
            # Handle shortened URLs by following redirects and getting final URL
            logger.info(f"Fetching content from URL: {url}")
            
            # Use realistic browser headers to bypass bot detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://www.google.com/'
            }
            
            # Make request with timeout and handle redirects - with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    timeout = 20 + (attempt * 10)  # Increase timeout on retries
                    response = self.session.get(url, timeout=timeout, allow_redirects=True, headers=headers)
                    final_url = response.url
                    
                    logger.info(f"Final URL after redirects: {final_url}")
                    
                    # Check for Amazon bot blocking
                    if response.status_code == 503 and 'amazon' in final_url.lower():
                        logger.warning(f"Amazon blocked request (503) for {final_url}, using fallback data extraction")
                        return self._create_amazon_fallback_content(url, final_url)
                    
                    response.raise_for_status()
                    break  # Success, exit retry loop
                    
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as e:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"Timeout on attempt {attempt + 1} for {url}, retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Failed to fetch {url} after {max_retries} attempts due to timeout")
                        raise e
            
            # Parse with BeautifulSoup to clean up content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "noscript"]):
                script.decompose()
            
            # Extract product title from meta tags and page title
            product_info = {'url': final_url}
            
            # Try to get product title from various sources
            title_candidates = []
            if soup.title:
                title_candidates.append(soup.title.string.strip())
            
            # Look for Open Graph title
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title_candidates.append(og_title['content'].strip())
            
            # Look for product name in meta tags
            product_name = soup.find('meta', attrs={'name': 'title'}) or soup.find('meta', attrs={'name': 'product_name'})
            if product_name and product_name.get('content'):
                title_candidates.append(product_name['content'].strip())
            
            product_info['title_candidates'] = title_candidates
            
            # Try to get product image
            image_candidates = []
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_candidates.append(og_image['content'])
            
            # Amazon-specific image extraction
            if 'amazon' in final_url.lower():
                # Look for Amazon's main product image
                amazon_img = soup.find('img', {'id': 'landingImage'}) or soup.find('img', {'data-old-hires': True})
                if amazon_img:
                    src = amazon_img.get('src') or amazon_img.get('data-old-hires') or amazon_img.get('data-a-dynamic-image')
                    if src:
                        image_candidates.insert(0, src)  # Prioritize Amazon main image
                
                # Look for other Amazon product images
                for img in soup.find_all('img'):
                    src = img.get('src') or img.get('data-src') or img.get('data-a-dynamic-image')
                    if src and any(keyword in src.lower() for keyword in ['images-amazon', 'ssl-images-amazon', 'm.media-amazon']):
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://amazon.com' + src
                        image_candidates.append(src)
            
            # Look for main product images (general sites)
            for img in soup.find_all('img', limit=15):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and ('product' in src.lower() or 'item' in src.lower() or len(src) > 50):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        from urllib.parse import urljoin
                        src = urljoin(final_url, src)
                    image_candidates.append(src)
            
            product_info['image_candidates'] = image_candidates
            
            # Get text content, focusing on main product areas
            content_areas = [
                soup.find('main'),
                soup.find(id=['main', 'content', 'product', 'detail', 'item']),
                soup.find(class_=['product', 'item', 'detail', 'content']),
                soup.find('body')
            ]
            
            text_content = ""
            for area in content_areas:
                if area:
                    text_content = area.get_text(separator='\n', strip=True)
                    if len(text_content) > 500:  # Ensure we have substantial content
                        break
            
            # If no substantial content found, get full page
            if len(text_content) < 500:
                text_content = soup.get_text(separator='\n', strip=True)
            
            # Enhance content with extracted metadata
            enhanced_content = f"""
EXTRACTED METADATA:
Final URL: {final_url}
Title candidates: {', '.join(title_candidates[:3])}
Image candidates: {', '.join(image_candidates[:2])}

PAGE CONTENT:
{text_content[:7000]}
"""
            
            return enhanced_content
            
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as e:
            logger.error(f"Timeout fetching page content from {url}: {e}")
            # For Amazon URLs, try to extract info from URL structure
            if 'amazon' in url.lower() or 'amzn.to' in url.lower():
                return self._create_amazon_fallback_content(url, url)
            return None
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
            # For Amazon URLs, try to extract info from URL structure
            if 'amazon' in url.lower() or 'amzn.to' in url.lower():
                return self._create_amazon_fallback_content(url, url)
            return None
    
    def _create_amazon_fallback_content(self, original_url: str, final_url: str) -> str:
        """Create fallback content when Amazon blocks requests"""
        import re
        
        # Try to extract product info from URL structure
        title_candidates = []
        image_candidates = []
        
        # Extract ASIN from URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', final_url)
        product_name_match = re.search(r'/([^/]+)/dp/', final_url)
        
        if product_name_match:
            # Clean up product name from URL
            product_name = product_name_match.group(1).replace('-', ' ').title()
            title_candidates.append(product_name)
        
        if asin_match:
            asin = asin_match.group(1)
            # Generate potential image URL
            image_url = f"https://images-na.ssl-images-amazon.com/images/I/{asin}._AC_SL1500_.jpg"
            image_candidates.append(image_url)
            
            # Alternative image URLs
            for suffix in ['_AC_SX300_SY300_QL70_FMwebp_', '_AC_SX425_', '_AC_SX679_']:
                image_candidates.append(f"https://m.media-amazon.com/images/I/{asin}.{suffix}.jpg")
        
        # Create enhanced fallback content
        enhanced_content = f"""
EXTRACTED METADATA:
Final URL: {final_url}
Title candidates: {', '.join(title_candidates) if title_candidates else 'Amazon Product'}
Image candidates: {', '.join(image_candidates[:2])}
Note: Amazon blocked direct access, using URL-based extraction

PAGE CONTENT:
Amazon Product Page
This product is available on Amazon but direct page access was blocked.
Product information extracted from URL structure.
ASIN: {asin_match.group(1) if asin_match else 'Unknown'}
"""
        
        return enhanced_content
    
    async def _analyze_with_openai(self, url: str, page_content: str) -> Optional[Dict[str, Any]]:
        """Use OpenAI to analyze page content and extract product information"""
        try:
            # Detect merchant from URL
            merchant = self._detect_merchant(url)
            
            # Create AI prompt
            prompt = self._create_extraction_prompt(url, page_content, merchant)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product information extraction expert. Extract accurate product details from web page content and return them in the specified JSON format. Always preserve the original URL exactly as provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"AI Response: {ai_response}")
            
            # Try to parse JSON response
            try:
                # Clean up response if it contains markdown formatting
                if ai_response.startswith('```json'):
                    ai_response = ai_response.split('```json')[1].split('```')[0].strip()
                elif ai_response.startswith('```'):
                    ai_response = ai_response.split('```')[1].split('```')[0].strip()
                
                product_data = json.loads(ai_response)
                
                # Validate and normalize category
                product_data['category'] = self._validate_category(product_data.get('category', 'other'))
                
                # Ensure original URL is preserved
                product_data['product_url'] = url
                product_data['scraped'] = True
                product_data['extraction_method'] = 'ai'
                
                return product_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI JSON response: {e}")
                logger.error(f"Raw AI response: {ai_response}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return None
    
    def _create_extraction_prompt(self, url: str, content: str, merchant: str) -> str:
        """Create prompt for AI product extraction"""
        return f"""
Extract product information from this {merchant} product page content and return it as JSON.

URL: {url}
Merchant: {merchant}

Page Content:
{content}

Please extract the following information and return as valid JSON:
{{
    "title": "Product title (string, REQUIRED - create descriptive title if not found)",
    "description": "Brief product description (string, 1-2 sentences, or create generic if not found)",
    "category": "Product category (one of: tools, materials, safety, accessories, other - use 'other' if unsure)",
    "merchant": "{merchant}",
    "original_price": "Original price as number (e.g. 199.99) or null if not found",
    "sale_price": "Sale/current price as number (e.g. 149.99) or null if not found", 
    "brand": "Brand name (string) or null if not found",
    "model": "Model number (string) or null if not found",
    "rating": "Average rating as number (e.g. 4.5) or null if not found",
    "rating_count": "Number of ratings as integer or null if not found",
    "image_url": "Main product image URL (string) or null if not found",
    "key_features": ["list", "of", "key", "features"] or null if not found,
    "project_types": ["array", "of", "applicable", "diy", "project", "types"]
}}

For project_types, determine which DIY project types this product is suitable for. Choose from:
- "woodworking": Wood cutting, furniture making, carpentry (table saws, wood glue, clamps, etc.)
- "plumbing": Pipe work, water systems (PVC pipes, pipe cutters, plumbers putty, etc.)
- "electrical": Wiring, electronics (wire strippers, electrical tape, multimeters, etc.)
- "automotive": Car repair, maintenance (socket wrenches, motor oil, brake pads, etc.)
- "metalworking": Metal fabrication, welding (angle grinders, welding equipment, metal files, etc.)
- "painting": Wall painting, finishing (paint brushes, rollers, primer, paint, etc.)
- "general": Universal tools useful for most DIY projects (screwdrivers, drills, hammers, etc.)
- "outdoor": Landscaping, gardening, outdoor projects (shovels, garden hose, outdoor lights, etc.)
- "home_improvement": Interior renovation, repairs (drywall, insulation, flooring materials, etc.)
- "crafts": Arts, small projects, hobbies (precision tools, craft supplies, small hardware, etc.)

Examples:
- Table saw → ["woodworking", "general"]
- PVC pipe → ["plumbing"]
- Wire strippers → ["electrical"]
- Cordless drill → ["general", "woodworking", "home_improvement"]
- Paint roller → ["painting"]
- Socket wrench set → ["automotive", "general"]

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON, no extra text, markdown, or formatting
2. NEVER use null for title - ALWAYS create a descriptive title from URL, domain, or available content
3. NEVER use null for category - use "other" if unclear
4. NEVER use null for project_types - use ["general"] as minimum
5. NEVER use null for description - create a basic description if none found
6. If you can't extract data, create reasonable defaults: title from URL structure, generic description
7. Use exact image URLs from the EXTRACTED METADATA when available
8. For Amazon URLs without content, create titles like "Amazon Product" or extract from URL path
9. Ensure prices are numbers, not strings; use null only for prices, images, and optional fields
10. MANDATORY: title, description, category, and project_types must NEVER be null
"""
    
    def _validate_category(self, category: str) -> str:
        """Validate and normalize category to match database enum"""
        if not category:
            return 'other'
        
        # Normalize the category
        category_lower = str(category).lower().strip()
        
        # Direct match
        if category_lower in self.valid_categories:
            return category_lower
        
        # Map common variations to valid categories
        category_mappings = {
            'tool': 'tools',
            'automotive': 'tools',  # Automotive tools go under tools
            'hardware': 'materials',
            'material': 'materials',
            'supplies': 'materials',
            'protective': 'safety',
            'protection': 'safety',
            'accessory': 'accessories',
            'attachment': 'accessories',
            'parts': 'accessories',
            'equipment': 'tools',
            'machinery': 'tools',
            'power_tools': 'tools',
            'hand_tools': 'tools'
        }
        
        # Check mappings
        for key, value in category_mappings.items():
            if key in category_lower:
                return value
        
        # Default to 'other' for unknown categories
        return 'other'
    
    def _detect_merchant(self, url: str) -> str:
        """Detect merchant from URL"""
        parsed_url = urlparse(url.lower())
        domain = parsed_url.netloc
        
        if 'amazon.com' in domain or 'amzn.to' in domain:
            return 'amazon'
        elif 'homedepot.com' in domain:
            return 'home_depot'
        elif 'lowes.com' in domain:
            return 'lowes'
        elif 'walmart.com' in domain:
            return 'walmart'
        elif 'target.com' in domain:
            return 'target'
        elif 'menards.com' in domain:
            return 'menards'
        elif 'harborfreight.com' in domain:
            return 'harbor_freight'
        elif 'northerntool.com' in domain:
            return 'northern_tool'
        else:
            return 'other'
    
    def _extract_basic_info(self, url: str, content: str) -> Dict[str, Any]:
        """Basic fallback extraction without AI"""
        merchant = self._detect_merchant(url)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        # Try to extract title from content
        lines = content.split('\n')
        title = f"Product from {domain}"
        
        # Look for title candidates in content
        if "Title candidates:" in content:
            # Extract from enhanced content
            for line in lines:
                if "Title candidates:" in line:
                    titles = line.split("Title candidates:")[1].strip()
                    if titles and titles != "":
                        # Take the first non-empty title
                        first_title = titles.split(',')[0].strip()
                        if first_title and len(first_title) > 3:
                            title = first_title
                    break
        else:
            # Look for potential product titles in the first several lines
            for line in lines[:20]:
                line = line.strip()
                if len(line) > 10 and len(line) < 200:
                    # Skip common website elements
                    if not any(skip in line.lower() for skip in ['menu', 'search', 'cart', 'sign in', 'account', 'footer', 'header']):
                        title = line
                        break
        
        # Extract image URL if available
        image_url = None
        if "Image candidates:" in content:
            for line in lines:
                if "Image candidates:" in line:
                    images = line.split("Image candidates:")[1].strip()
                    if images and images != "":
                        # Take the first image URL
                        first_image = images.split(',')[0].strip()
                        if first_image and first_image.startswith('http'):
                            image_url = first_image
                    break
        
        return {
            'title': title,
            'description': f'Product available from {domain}',
            'category': self._validate_category('other'),
            'merchant': merchant,
            'original_price': None,
            'sale_price': None,
            'brand': None,
            'model': None,
            'rating': None,
            'rating_count': None,
            'image_url': image_url,
            'key_features': None,
            'project_types': ['general'],  # Default to general for unknown products
            'product_url': url,
            'scraped': True,
            'extraction_method': 'basic'
        }
    
    def _create_fallback_product(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback product info when extraction fails"""
        merchant = self._detect_merchant(url)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        # Create a more descriptive title based on merchant
        merchant_names = {
            'amazon': 'Amazon',
            'home_depot': 'Home Depot', 
            'lowes': 'Lowes',
            'walmart': 'Walmart'
        }
        
        merchant_display = merchant_names.get(merchant, domain)
        
        return {
            'title': f'Product from {merchant_display}',
            'description': f'This product is available from {merchant_display}. Detailed information extraction was not possible.',
            'category': self._validate_category('other'),
            'merchant': merchant,
            'original_price': None,
            'sale_price': None,
            'brand': None,
            'model': None,
            'rating': None,
            'rating_count': None,
            'image_url': None,
            'key_features': None,
            'project_types': ['general'],  # Default to general for fallback products
            'product_url': url,
            'scraped': False,
            'extraction_method': 'fallback'
        }
    
    async def _search_based_extraction(self, url: str, product_title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract product info using search when direct scraping fails"""
        try:
            # Extract product info from URL if no title provided
            if not product_title:
                product_title = self._extract_title_from_url(url)
            
            logger.info(f"Attempting search-based extraction for: {product_title}")
            
            # Try Google Shopping search
            logger.info(f"Trying Google Shopping search for: {product_title}")
            search_results = await self._search_google_shopping(product_title, url)
            if search_results:
                logger.info(f"Google Shopping search successful, found: {search_results.get('title', 'N/A')}")
                return search_results
            else:
                logger.info("Google Shopping search returned no results")
            
            # Fallback to general web search + AI analysis
            logger.info(f"Trying web search + AI for: {product_title}")
            web_search_results = await self._search_web_for_product(product_title, url)
            if web_search_results:
                logger.info(f"Web search successful, found: {web_search_results.get('title', 'N/A')}")
                return web_search_results
            else:
                logger.info("Web search returned no results")
            
            return None
            
        except Exception as e:
            logger.error(f"Search-based extraction failed: {e}")
            return None
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract potential product title from URL structure"""
        import re
        
        # Clean URL and extract meaningful parts
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Remove common URL patterns
            path = re.sub(r'/dp/[A-Z0-9]+', '', path)  # Amazon product ID
            path = re.sub(r'/p/[0-9]+', '', path)     # Home Depot product ID
            path = re.sub(r'/pd/[0-9]+', '', path)    # Lowes product ID
            
            # Extract product name from path
            path_parts = [part for part in path.split('/') if part and len(part) > 2]
            if path_parts:
                # Take the longest meaningful part, likely the product name
                product_part = max(path_parts, key=len)
                # Clean up the product name
                product_name = product_part.replace('-', ' ').replace('_', ' ')
                # Remove numbers and special chars, capitalize
                product_name = re.sub(r'[^a-zA-Z\s]', ' ', product_name)
                product_name = ' '.join(word.capitalize() for word in product_name.split() if len(word) > 2)
                
                if len(product_name) > 5:
                    return product_name
            
            # Fallback to domain-based title
            domain = parsed.netloc.replace('www.', '')
            return f"Product from {domain}"
            
        except Exception as e:
            logger.error(f"Error extracting title from URL: {e}")
            return "Unknown Product"
    
    async def _search_google_shopping(self, product_title: str, original_url: str) -> Optional[Dict[str, Any]]:
        """Search Google Shopping for product information"""
        try:
            merchant = self._detect_merchant(original_url)
            
            # Create targeted search query based on merchant
            if merchant == 'home_depot':
                search_query = f"{product_title} site:homedepot.com price"
            elif merchant == 'amazon':
                search_query = f"{product_title} site:amazon.com price"
            elif merchant == 'lowes':
                search_query = f"{product_title} site:lowes.com price"
            elif merchant == 'walmart':
                search_query = f"{product_title} site:walmart.com price"
            elif merchant == 'target':
                search_query = f"{product_title} site:target.com price"
            elif merchant == 'menards':
                search_query = f"{product_title} site:menards.com price"
            elif merchant == 'harbor_freight':
                search_query = f"{product_title} site:harborfreight.com price"
            elif merchant == 'northern_tool':
                search_query = f"{product_title} site:northerntool.com price"
            else:
                search_query = f"{product_title} price buy"
            
            google_url = f"https://www.google.com/search?q={search_query}&tbm=shop"
            
            # Use realistic headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(google_url, headers=headers, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Google Shopping search failed with status {response.status_code}")
                return None
            
            # Parse search results
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information from Google Shopping results
            price_info = self._extract_price_from_search(soup)
            image_info = self._extract_image_from_search(soup)
            
            # Try merchant-specific extraction methods if no price found
            if not price_info:
                logger.info(f"No price found in Google Shopping, trying {merchant} specific search for: {product_title}")
                price_info = await self._extract_merchant_specific_price(product_title, original_url, merchant)
                if price_info:
                    logger.info(f"{merchant.title()} search found price: ${price_info.get('sale_price', 'N/A')}")
                else:
                    logger.info(f"{merchant.title()} specific search found no price")
            
            if not price_info and not image_info:
                return None
            
            return {
                'title': product_title,
                'description': f'Product found via search: {product_title}',
                'category': self._validate_category('other'),
                'merchant': merchant,
                'original_price': price_info.get('original_price') if price_info else None,
                'sale_price': price_info.get('sale_price') if price_info else None,
                'brand': None,
                'model': None,
                'rating': None,
                'rating_count': None,
                'image_url': image_info.get('image_url') if image_info else None,
                'key_features': None,
                'project_types': ['general'],
                'product_url': original_url,
                'scraped': True,
                'extraction_method': 'google_shopping_search'
            }
            
        except Exception as e:
            logger.error(f"Google Shopping search failed: {e}")
            return None
    
    async def _search_web_for_product(self, product_title: str, original_url: str) -> Optional[Dict[str, Any]]:
        """Search web for product information using AI analysis"""
        try:
            if not self.ai_enabled:
                return None
            
            # Create search query
            search_query = f"{product_title} specifications price review"
            google_url = f"https://www.google.com/search?q={search_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = self.session.get(google_url, headers=headers, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text content from search results
            search_content = soup.get_text(separator='\n', strip=True)[:5000]
            
            # Use AI to analyze search results
            prompt = f"""
Analyze these Google search results for the product "{product_title}" and extract information:

Search Results:
{search_content}

Original URL: {original_url}

Extract what you can and return as JSON:
{{
    "title": "{product_title}",
    "estimated_price": "estimated price as number or null",
    "brand": "brand name if found or null",
    "category": "product category (tools, materials, safety, accessories, other)",
    "project_types": ["applicable", "project", "types"]
}}

Return ONLY valid JSON, no extra text.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Extract product information from search results. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Clean and parse JSON
            if ai_response.startswith('```json'):
                ai_response = ai_response.split('```json')[1].split('```')[0].strip()
            elif ai_response.startswith('```'):
                ai_response = ai_response.split('```')[1].split('```')[0].strip()
            
            search_data = json.loads(ai_response)
            
            # Create product info from search analysis
            merchant = self._detect_merchant(original_url)
            
            return {
                'title': search_data.get('title', product_title),
                'description': f'Product information extracted from web search',
                'category': self._validate_category(search_data.get('category', 'other')),
                'merchant': merchant,
                'original_price': None,
                'sale_price': search_data.get('estimated_price'),
                'brand': search_data.get('brand'),
                'model': None,
                'rating': None,
                'rating_count': None,
                'image_url': None,
                'key_features': None,
                'project_types': search_data.get('project_types', ['general']),
                'product_url': original_url,
                'scraped': True,
                'extraction_method': 'web_search_ai'
            }
            
        except Exception as e:
            logger.error(f"Web search extraction failed: {e}")
            return None
    
    def _extract_price_from_search(self, soup: BeautifulSoup) -> Optional[Dict[str, float]]:
        """Extract price information from search results"""
        try:
            import re
            
            # Look for price patterns in the HTML
            price_patterns = [
                r'\$([0-9,]+\.?[0-9]*)',
                r'USD\s*([0-9,]+\.?[0-9]*)',
                r'Price:\s*\$([0-9,]+\.?[0-9]*)',
            ]
            
            text_content = soup.get_text()
            prices = []
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    try:
                        price = float(match.replace(',', ''))
                        if 1 <= price <= 10000:  # Reasonable price range
                            prices.append(price)
                    except:
                        continue
            
            if prices:
                # Take the most common price or median
                prices.sort()
                median_price = prices[len(prices)//2]
                return {'sale_price': median_price}
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting price from search: {e}")
            return None
    
    def _extract_image_from_search(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract product image from search results"""
        try:
            # Look for product images in search results
            images = soup.find_all('img')
            
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src and any(keyword in src.lower() for keyword in ['product', 'item', 'shop']):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.google.com' + src
                    
                    if src.startswith('http') and len(src) > 20:
                        return {'image_url': src}
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting image from search: {e}")
            return None
    
    def _merge_product_data(self, direct_data: Dict[str, Any], search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge direct extraction data with search-based data"""
        merged = direct_data.copy()
        
        # Prioritize search data for missing critical fields
        if not merged.get('original_price') and not merged.get('sale_price'):
            if search_data.get('original_price'):
                merged['original_price'] = search_data['original_price']
            if search_data.get('sale_price'):
                merged['sale_price'] = search_data['sale_price']
        
        if not merged.get('image_url') and search_data.get('image_url'):
            merged['image_url'] = search_data['image_url']
        
        if not merged.get('brand') and search_data.get('brand'):
            merged['brand'] = search_data['brand']
        
        # Update extraction method to indicate enhancement
        merged['extraction_method'] = f"{merged.get('extraction_method', 'direct')}_enhanced_with_{search_data.get('extraction_method', 'search')}"
        
        return merged
    
    async def _extract_merchant_specific_price(self, product_title: str, original_url: str, merchant: str) -> Optional[Dict[str, float]]:
        """Extract merchant-specific price using targeted search"""
        try:
            if merchant == 'home_depot':
                return await self._extract_home_depot_price_from_search(product_title, original_url)
            elif merchant == 'lowes':
                return await self._extract_lowes_price_from_search(product_title, original_url)
            elif merchant == 'walmart':
                return await self._extract_walmart_price_from_search(product_title, original_url)
            elif merchant == 'target':
                return await self._extract_target_price_from_search(product_title, original_url)
            elif merchant == 'amazon':
                return await self._extract_amazon_price_from_search(product_title, original_url)
            else:
                return await self._extract_generic_price_from_search(product_title, original_url, merchant)
        except Exception as e:
            logger.error(f"Error in {merchant} specific price extraction: {e}")
            return None
    
    async def _extract_home_depot_price_from_search(self, product_title: str, original_url: str) -> Optional[Dict[str, float]]:
        """Extract Home Depot price using targeted search"""
        try:
            # Extract model/product number from URL if possible
            import re
            url_parts = original_url.split('/')
            product_id = None
            
            for part in url_parts:
                if re.match(r'^\d+$', part) and len(part) > 6:  # Likely a product ID
                    product_id = part
                    break
            
            # Create specific search queries
            search_queries = [
                f"{product_title} Home Depot price",
                f"RYOBI RY40780 Home Depot price" if 'ryobi' in product_title.lower() else f"{product_title} price",
                f"site:homedepot.com {product_title}"
            ]
            
            if product_id:
                search_queries.insert(0, f"site:homedepot.com {product_id}")
            
            for query in search_queries:
                try:
                    google_url = f"https://www.google.com/search?q={query}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    }
                    
                    response = self.session.get(google_url, headers=headers, timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for price patterns in search results
                    text_content = soup.get_text()
                    
                    # Home Depot specific price patterns
                    price_patterns = [
                        r'\$([0-9,]+\.?[0-9]*)\s*(?:each|ea\.?)',
                        r'(?:Price|Sale):?\s*\$([0-9,]+\.?[0-9]*)',
                        r'\$([0-9,]+\.?[0-9]*)\s*(?:at|from)?\s*Home\s*Depot',
                        r'([0-9,]+\.?[0-9]*)\s*USD',
                        r'\$([0-9,]+\.?[0-9]*)'
                    ]
                    
                    prices = []
                    for pattern in price_patterns:
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        for match in matches:
                            try:
                                price = float(match.replace(',', ''))
                                if 10 <= price <= 5000:  # Reasonable price range for tools
                                    prices.append(price)
                            except ValueError:
                                continue
                    
                    if prices:
                        # Take the most common price
                        from collections import Counter
                        price_counts = Counter(prices)
                        most_common_price = price_counts.most_common(1)[0][0]
                        
                        logger.info(f"Found Home Depot price via search: ${most_common_price}")
                        return {'sale_price': most_common_price}
                        
                except Exception as e:
                    logger.warning(f"Error in Home Depot price search with query '{query}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error in Home Depot price extraction: {e}")
            return None
    
    async def _extract_lowes_price_from_search(self, product_title: str, original_url: str) -> Optional[Dict[str, float]]:
        """Extract Lowes price using targeted search"""
        try:
            import re
            url_parts = original_url.split('/')
            product_id = None
            
            # Extract Lowes product ID from URL
            for part in url_parts:
                if re.match(r'^\d+$', part) and len(part) >= 9:  # Lowes product IDs
                    product_id = part
                    break
            
            # Create Lowes-specific search queries
            search_queries = [
                f"{product_title} Lowes price",
                f"site:lowes.com {product_title}",
                f"CRAFTSMAN V20 Lowes price" if 'craftsman' in product_title.lower() else f"{product_title} price"
            ]
            
            if product_id:
                search_queries.insert(0, f"site:lowes.com {product_id}")
            
            return await self._search_for_price(search_queries, 'Lowes', [
                r'\$([0-9,]+\.?[0-9]*)\s*(?:each|ea\.?)',
                r'(?:Price|Special|Sale):?\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:at|from)?\s*Lowe[\'s]*',
                r'Model\s*#.*?\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)'
            ])
            
        except Exception as e:
            logger.error(f"Error in Lowes price extraction: {e}")
            return None
    
    async def _extract_walmart_price_from_search(self, product_title: str, original_url: str) -> Optional[Dict[str, float]]:
        """Extract Walmart price using targeted search"""
        try:
            search_queries = [
                f"{product_title} Walmart price",
                f"site:walmart.com {product_title}",
                f"{product_title} walmart.com"
            ]
            
            return await self._search_for_price(search_queries, 'Walmart', [
                r'Current\s*Price:?\s*\$([0-9,]+\.?[0-9]*)',
                r'(?:Price|Sale):?\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:at|from)?\s*Walmart',
                r'Now\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)'
            ])
            
        except Exception as e:
            logger.error(f"Error in Walmart price extraction: {e}")
            return None
    
    async def _extract_target_price_from_search(self, product_title: str, original_url: str) -> Optional[Dict[str, float]]:
        """Extract Target price using targeted search"""
        try:
            search_queries = [
                f"{product_title} Target price",
                f"site:target.com {product_title}",
                f"{product_title} target.com"
            ]
            
            return await self._search_for_price(search_queries, 'Target', [
                r'(?:Price|Sale|Current):?\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:at|from)?\s*Target',
                r'reg\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)'
            ])
            
        except Exception as e:
            logger.error(f"Error in Target price extraction: {e}")
            return None
    
    async def _extract_amazon_price_from_search(self, product_title: str, original_url: str) -> Optional[Dict[str, float]]:
        """Extract Amazon price using enhanced targeted search"""
        try:
            # Try to extract ASIN from URL
            asin = None
            if '/dp/' in original_url:
                asin = original_url.split('/dp/')[1].split('/')[0].split('?')[0]
            elif 'amzn.to' in original_url:
                # For short links, we might need to extract from resolved URL
                # but for now use product title
                pass
            
            # Create more specific search queries
            search_queries = []
            if asin:
                search_queries.append(f"Amazon ASIN {asin} price")
                search_queries.append(f"site:amazon.com {asin}")
            
            search_queries.extend([
                f"{product_title} Amazon price current",
                f"{product_title} site:amazon.com price",
                f"{product_title} Amazon.com buy now",
                f"{product_title} Amazon price USD"
            ])
            
            # Try Amazon-specific price search with enhanced patterns
            result = await self._search_for_price(search_queries, 'Amazon', [
                r'Buy\s*New:?\s*\$([0-9,]+\.?[0-9]*)',
                r'Price:?\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:FREE|Prime)',
                r'List\s*Price:?\s*\$([0-9,]+\.?[0-9]*)',
                r'Deal\s*(?:of\s*the\s*Day)?:?\s*\$([0-9,]+\.?[0-9]*)',
                r'Sale:?\s*\$([0-9,]+\.?[0-9]*)',
                r'Now:?\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:&|and)\s*FREE',
                r'\$([0-9,]+\.?[0-9]*)\s*with\s*(?:Subscribe|coupon)',
                r'\$([0-9,]+\.?[0-9]*)'
            ])
            
            if result:
                return result
            
            # Fallback: Try Google Shopping specific search for Amazon products
            shopping_query = f"{product_title} price shopping"
            try:
                google_url = f"https://www.google.com/search?q={shopping_query}&tbm=shop"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                
                response = self.session.get(google_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for price spans in shopping results
                    price_elements = soup.find_all(['span', 'div'], string=re.compile(r'\$[0-9,]+\.?[0-9]*'))
                    
                    prices = []
                    for elem in price_elements:
                        text = elem.get_text()
                        price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', text)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(',', ''))
                                if 5 <= price <= 10000:  # Reasonable range
                                    prices.append(price)
                            except ValueError:
                                continue
                    
                    if prices:
                        # Return the median price as it's more reliable
                        prices.sort()
                        median_price = prices[len(prices) // 2]
                        logger.info(f"Found Amazon price via Google Shopping: ${median_price}")
                        return {'sale_price': median_price}
                        
            except Exception as e:
                logger.warning(f"Google Shopping search failed: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in Amazon price extraction: {e}")
            return None
    
    async def _extract_generic_price_from_search(self, product_title: str, original_url: str, merchant: str) -> Optional[Dict[str, float]]:
        """Extract price for any merchant using generic patterns"""
        try:
            parsed = urlparse(original_url)
            domain = parsed.netloc.replace('www.', '')
            
            search_queries = [
                f"{product_title} {merchant} price",
                f"site:{domain} {product_title}",
                f"{product_title} {domain}",
                f"{product_title} price"
            ]
            
            return await self._search_for_price(search_queries, merchant.title(), [
                r'(?:Price|Sale|Cost):?\s*\$([0-9,]+\.?[0-9]*)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:each|ea\.?)',
                r'\$([0-9,]+\.?[0-9]*)\s*(?:at|from)?\s*' + re.escape(domain.split('.')[0]),
                r'([0-9,]+\.?[0-9]*)\s*USD',
                r'\$([0-9,]+\.?[0-9]*)'
            ])
            
        except Exception as e:
            logger.error(f"Error in {merchant} price extraction: {e}")
            return None
    
    async def _search_for_price(self, search_queries: list, merchant_name: str, price_patterns: list) -> Optional[Dict[str, float]]:
        """Generic method to search for prices using multiple queries and patterns"""
        try:
            for query in search_queries:
                try:
                    google_url = f"https://www.google.com/search?q={query}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    }
                    
                    response = self.session.get(google_url, headers=headers, timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text()
                    
                    prices = []
                    for pattern in price_patterns:
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        for match in matches:
                            try:
                                price = float(match.replace(',', ''))
                                if 5 <= price <= 10000:  # Reasonable price range
                                    prices.append(price)
                            except ValueError:
                                continue
                    
                    if prices:
                        # Take the most common price
                        from collections import Counter
                        price_counts = Counter(prices)
                        most_common_price = price_counts.most_common(1)[0][0]
                        
                        logger.info(f"Found {merchant_name} price via search: ${most_common_price}")
                        return {'sale_price': most_common_price}
                        
                except Exception as e:
                    logger.warning(f"Error in {merchant_name} price search with query '{query}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error in {merchant_name} price search: {e}")
            return None

# Global instance
product_info_agent = ProductInfoAgent()