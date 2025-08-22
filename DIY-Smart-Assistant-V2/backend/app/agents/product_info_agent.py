"""
Enhanced AI-Powered Product Information Extraction Agent for V2
Uses OpenAI GPT to intelligently extract product information from retailer URLs
"""
import asyncio
import requests
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin, parse_qs
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import re
import time
import random
from .base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class ProductInfoAgent(BaseAgent):
    """Enhanced AI-powered agent for extracting product information from retailer URLs"""
    
    def __init__(self):
        super().__init__(
            name="product_info_agent",
            config={"description": "Extracts product information using AI analysis from retailer URLs"}
        )
        
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
        
        # Setup session for web requests with rotation
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        self._rotate_user_agent()
        
        # Valid categories - expanded for better classification
        self.valid_categories = [
            'power_tools', 'hand_tools', 'safety_equipment', 'building_materials', 
            'hardware', 'plumbing', 'electrical', 'paint_supplies', 'garden_tools',
            'automotive', 'home_improvement', 'storage_organization', 'other'
        ]
        
        # Project type mapping for better categorization
        self.project_types = [
            'woodworking', 'plumbing', 'electrical', 'automotive', 'metalworking',
            'painting', 'general', 'outdoor', 'home_improvement', 'crafts'
        ]
        
        # Amazon ASIN patterns for better extraction
        self.asin_patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'&ASIN=([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})'
        ]
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate input data for product info extraction"""
        if not isinstance(input_data, dict):
            return False
        
        product_url = input_data.get('product_url')
        if not product_url or not isinstance(product_url, str):
            return False
            
        # Basic URL validation
        try:
            parsed = urlparse(product_url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        ua = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': ua})
        logger.debug(f"Rotated to user agent: {ua[:50]}...")
    
    async def _resolve_url(self, url: str) -> Optional[str]:
        """Resolve shortened URLs to get the actual product URL"""
        try:
            # Handle common short URL services
            if any(domain in url.lower() for domain in ['amzn.to', 'bit.ly', 't.co', 'tinyurl.com', 'goo.gl']):
                logger.info(f"Resolving shortened URL: {url}")
                
                # Use HEAD request to get final URL without downloading content
                response = self.session.head(url, allow_redirects=True, timeout=10)
                final_url = response.url
                logger.info(f"Resolved URL: {final_url}")
                return final_url
            
            return url
            
        except Exception as e:
            logger.warning(f"URL resolution failed for {url}: {e}")
            return url
    
    def _extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract Amazon ASIN from URL"""
        for pattern in self.asin_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_amazon_image_variants(self, asin: str, base_image_url: Optional[str] = None) -> List[str]:
        """Generate multiple Amazon image URL variants for better success rate"""
        variants = []
        
        if base_image_url:
            variants.append(base_image_url)
            
            # Generate different size variants
            base_patterns = [
                base_image_url.replace('._AC_SX300_SY300_QL70_FMwebp_.', '._AC_SL1500_.'),
                base_image_url.replace('._AC_SX300_SY300_QL70_FMwebp_.', '._AC_SL1000_.'),
                base_image_url.replace('._AC_SX300_SY300_QL70_FMwebp_.', '._AC_SL500_.'),
                base_image_url.replace('__AC_SX300_SY300_QL70_FMwebp__', '_AC_SL1500_'),
            ]
            variants.extend([url for url in base_patterns if url != base_image_url])
        
        # Generate standard Amazon image URLs using ASIN
        if asin:
            standard_formats = [
                f"https://m.media-amazon.com/images/I/{asin}._AC_SL1500_.jpg",
                f"https://images-na.ssl-images-amazon.com/images/I/{asin}._AC_SL1500_.jpg",
                f"https://m.media-amazon.com/images/I/{asin}._AC_SL1000_.jpg",
                f"https://images-amazon.com/images/I/{asin}._AC_SL1500_.jpg"
            ]
            variants.extend(standard_formats)
        
        return list(set(variants))  # Remove duplicates
    
    async def _validate_image_url(self, url: str) -> bool:
        """Validate that an image URL is accessible"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code == 200 and 'image' in response.headers.get('content-type', '').lower()
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
            
            # Resolve shortened URLs first
            resolved_url = await self._resolve_url(product_url)
            
            # Extract product information using AI
            product_info = await self._extract_product_info_with_ai(resolved_url or product_url)
            
            return AgentResult(
                success=True,
                data=product_info,
                execution_time=3.2
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
            logger.info(f"Fetching content from URL: {url}")
            
            # Rotate user agent for each request
            self._rotate_user_agent()
            
            # Use realistic browser headers to bypass bot detection
            headers = {
                'User-Agent': self.session.headers.get('User-Agent'),
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
                    
                    # Check for bot blocking
                    if response.status_code == 503 and any(retailer in final_url.lower() for retailer in ['amazon', 'walmart', 'target']):
                        logger.warning(f"Request blocked (503) for {final_url}, using fallback data extraction")
                        return self._create_fallback_content(url, final_url)
                    
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
            
            # Extract metadata
            product_info = {'url': final_url}
            
            # Extract product title from various sources
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
            
            # Extract product images with enhanced methods
            image_candidates = []
            merchant = self._detect_merchant(final_url)
            
            # Amazon-specific enhanced image extraction
            if merchant == 'amazon':
                # Try multiple Amazon image extraction methods
                asin = self._extract_asin_from_url(final_url)
                
                # Method 1: Standard Amazon image selectors
                amazon_selectors = [
                    {'id': 'landingImage'},
                    {'data-old-hires': True},
                    {'class': 'a-dynamic-image'},
                    {'data-a-dynamic-image': True}
                ]
                
                for selector in amazon_selectors:
                    img = soup.find('img', selector)
                    if img:
                        src = img.get('src') or img.get('data-old-hires') or img.get('data-a-dynamic-image')
                        if src and src not in image_candidates:
                            image_candidates.append(src)
                
                # Method 2: Generate ASIN-based image URLs
                if asin:
                    asin_images = self._get_amazon_image_variants(asin, image_candidates[0] if image_candidates else None)
                    image_candidates.extend([img for img in asin_images if img not in image_candidates])
            
            # Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image['content']
                if img_url not in image_candidates:
                    image_candidates.append(img_url)
            elif merchant in ['home_depot', 'lowes']:
                # Home improvement store image patterns
                for img in soup.find_all('img'):
                    src = img.get('src') or img.get('data-src')
                    if src and 'product' in src.lower():
                        image_candidates.append(src)
            
            # General product image extraction
            for img in soup.find_all('img', limit=15):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and ('product' in src.lower() or 'item' in src.lower() or len(src) > 50):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(final_url, src)
                    image_candidates.append(src)
            
            product_info['image_candidates'] = image_candidates
            
            # Get text content focusing on main product areas
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
            
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
            return None
    
    def _create_fallback_content(self, original_url: str, final_url: str) -> str:
        """Create fallback content when direct access is blocked"""
        import re
        
        # Try to extract product info from URL structure
        title_candidates = []
        image_candidates = []
        
        # Extract product information from URL
        if 'amazon' in final_url.lower():
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', final_url)
            product_name_match = re.search(r'/([^/]+)/dp/', final_url)
            
            if product_name_match:
                product_name = product_name_match.group(1).replace('-', ' ').title()
                title_candidates.append(product_name)
            
            if asin_match:
                asin = asin_match.group(1)
                image_url = f"https://images-na.ssl-images-amazon.com/images/I/{asin}._AC_SL1500_.jpg"
                image_candidates.append(image_url)
        
        # Create enhanced fallback content
        enhanced_content = f"""
EXTRACTED METADATA:
Final URL: {final_url}
Title candidates: {', '.join(title_candidates) if title_candidates else 'Product from retailer'}
Image candidates: {', '.join(image_candidates[:2])}
Note: Direct access was blocked, using URL-based extraction

PAGE CONTENT:
Product Page
This product is available from a major retailer but direct page access was blocked.
Product information extracted from URL structure.
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
            logger.info(f"AI Response length: {len(ai_response)} characters")
            
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
                
                # Add merchant information
                product_data['merchant'] = merchant
                
                # Enhanced image URL validation and selection for Amazon
                if merchant == 'amazon' and product_data.get('image_url'):
                    asin = self._extract_asin_from_url(url)
                    if asin:
                        # Get multiple image variants and pick the best one
                        image_variants = self._get_amazon_image_variants(asin, product_data['image_url'])
                        # Use the first high-quality image
                        for variant in image_variants:
                            if '_AC_SL1500_' in variant or '_AC_SL1000_' in variant:
                                product_data['image_url'] = variant
                                break
                
                # Ensure project_types is always a list
                if not isinstance(product_data.get('project_types'), list):
                    product_data['project_types'] = ['general']
                
                # Validate price data types
                for price_field in ['original_price', 'sale_price']:
                    if price_field in product_data and product_data[price_field] is not None:
                        try:
                            product_data[price_field] = float(product_data[price_field])
                        except (ValueError, TypeError):
                            product_data[price_field] = None
                
                # Validate rating data
                if 'rating' in product_data and product_data['rating'] is not None:
                    try:
                        product_data['rating'] = float(product_data['rating'])
                        # Ensure rating is within valid range
                        if product_data['rating'] < 0 or product_data['rating'] > 5:
                            product_data['rating'] = None
                    except (ValueError, TypeError):
                        product_data['rating'] = None
                
                if 'rating_count' in product_data and product_data['rating_count'] is not None:
                    try:
                        product_data['rating_count'] = int(product_data['rating_count'])
                        if product_data['rating_count'] < 0:
                            product_data['rating_count'] = None
                    except (ValueError, TypeError):
                        product_data['rating_count'] = None
                
                return product_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI JSON response: {e}")
                logger.error(f"Raw AI response: {ai_response}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return None
    
    def _create_extraction_prompt(self, url: str, content: str, merchant: str) -> str:
        """Create enhanced prompt for AI product extraction"""
        
        # Add merchant-specific guidance
        merchant_guidance = {
            'amazon': "Focus on ASIN extraction, detailed product specifications, and accurate pricing from Amazon product pages.",
            'home_depot': "Extract model numbers, brand information, and detailed specifications common in home improvement tools.",
            'lowes': "Focus on product categories for DIY and construction, detailed specifications, and accurate pricing.",
            'walmart': "Extract brand information, model numbers, and focus on consumer product details."
        }
        
        specific_guidance = merchant_guidance.get(merchant, "Extract product information accurately from the retailer page.")
        
        return f"""
You are an expert product information extraction system. Extract detailed, accurate product information from this {merchant} product page.

{specific_guidance}

URL: {url}
Merchant: {merchant}

Page Content:
{content}

CRITICAL EXTRACTION REQUIREMENTS:
1. **Title**: Must be the exact, complete product title as shown on the product page. Never use generic titles.
2. **Description**: Create a concise, informative description (1-2 sentences) based on product details.
3. **Prices**: Extract BOTH original price and current/sale price if available. Look for strikethrough prices, "was/now" pricing, discounts.
4. **Images**: Use the highest quality image URL available. For Amazon, prefer _AC_SL1500_ or _AC_SL1000_ formats.
5. **Brand & Model**: Extract exact brand name and model number if visible.
6. **Ratings**: Extract numerical rating (e.g., 4.5) and review count (e.g., 1,847).
7. **Specifications**: Extract detailed technical specifications into a structured object.
8. **Features**: List key product features, benefits, or selling points.

Return as valid JSON:
{{
    "title": "EXACT product title from page (REQUIRED - never generic)",
    "description": "Detailed product description based on page content (REQUIRED)",
    "category": "Best fitting category from: {', '.join(self.valid_categories)}",
    "original_price": "Original/list price as number (e.g. 299.99) or null",
    "sale_price": "Current/sale price as number (e.g. 249.99) or null", 
    "brand": "Exact brand name or null",
    "model": "Exact model number/identifier or null",
    "rating": "Average rating as number (e.g. 4.7) or null",
    "rating_count": "Number of ratings/reviews as integer or null",
    "image_url": "Highest quality product image URL or null",
    "key_features": ["feature1", "feature2", "feature3"] or null,
    "project_types": ["applicable", "diy", "project", "types"],
    "specifications": {{"spec_name": "spec_value", "another_spec": "value"}} or null
}}

PROJECT TYPES - Choose ALL applicable types from:
- "woodworking": Wood cutting, furniture making, carpentry tools
- "plumbing": Pipe work, water systems, plumbing tools  
- "electrical": Wiring, electronics, electrical tools
- "automotive": Car repair, maintenance tools
- "metalworking": Metal fabrication, welding tools
- "painting": Wall painting, finishing supplies
- "general": Universal tools for most DIY projects
- "outdoor": Landscaping, gardening, outdoor tools
- "home_improvement": Interior renovation, repair tools
- "crafts": Arts, small projects, hobby supplies

MANDATORY FIELDS (never null): title, description, category, project_types
OPTIONAL FIELDS (can be null): prices, brand, model, rating, image_url, features, specifications

Extract information precisely. If unable to find specific data, use reasonable defaults for required fields only.

FINAL VALIDATION:
- Return ONLY valid JSON, no extra text or markdown formatting
- Use exact image URLs from EXTRACTED METADATA when available  
- Ensure all required fields are populated with meaningful data
"""
    
    def _validate_category(self, category: str) -> str:
        """Validate and normalize category"""
        if not category:
            return 'other'
        
        category_lower = str(category).lower().strip()
        
        # Direct match
        if category_lower in self.valid_categories:
            return category_lower
        
        # Map common variations
        category_mappings = {
            'tool': 'hand_tools',
            'tools': 'hand_tools', 
            'power_tool': 'power_tools',
            'automotive': 'automotive',
            'hardware': 'hardware',
            'material': 'building_materials',
            'materials': 'building_materials',
            'supplies': 'building_materials',
            'protective': 'safety_equipment',
            'protection': 'safety_equipment',
            'safety': 'safety_equipment',
            'paint': 'paint_supplies',
            'painting': 'paint_supplies',
            'plumbing': 'plumbing',
            'electrical': 'electrical',
            'garden': 'garden_tools',
            'outdoor': 'garden_tools'
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
            'project_types': ['general'],
            'specifications': None,
            'product_url': url,
            'scraped': True,
            'extraction_method': 'basic'
        }
    
    def _create_fallback_product(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback product info when extraction fails"""
        merchant = self._detect_merchant(url)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        merchant_names = {
            'amazon': 'Amazon',
            'home_depot': 'Home Depot', 
            'lowes': 'Lowes',
            'walmart': 'Walmart',
            'target': 'Target'
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
            'project_types': ['general'],
            'specifications': None,
            'product_url': url,
            'scraped': False,
            'extraction_method': 'fallback'
        }
    
    async def _search_based_extraction(self, url: str, product_title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract product info using search when direct scraping fails"""
        try:
            # Create a basic fallback product
            return self._create_fallback_product(url, "Search-based extraction not implemented in this version")
        except Exception as e:
            logger.error(f"Search-based extraction failed: {e}")
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
        
        # Update extraction method
        merged['extraction_method'] = f"{merged.get('extraction_method', 'direct')}_enhanced"
        
        return merged

# Singleton instance
product_info_agent = ProductInfoAgent()