"""
Product information scraper service
Automatically extracts product details from URLs
"""
import requests
import re
import json
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ProductScraper:
    """Service for scraping product information from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_product_info(self, url: str) -> Dict[str, Any]:
        """
        Scrape product information from a given URL
        
        Args:
            url: Product URL to scrape
            
        Returns:
            Dictionary containing product information
        """
        try:
            # Parse URL to determine merchant
            parsed_url = urlparse(url.lower())
            domain = parsed_url.netloc
            
            # Route to appropriate scraper based on domain
            if 'amazon.com' in domain or 'amzn.to' in domain:
                return self._scrape_amazon(url)
            elif 'homedepot.com' in domain:
                return self._scrape_home_depot(url)
            elif 'lowes.com' in domain:
                return self._scrape_lowes(url)
            elif 'walmart.com' in domain:
                return self._scrape_walmart(url)
            else:
                return self._scrape_generic(url)
                
        except Exception as e:
            logger.error(f"Error scraping product from {url}: {e}")
            return self._create_fallback_product(url)
    
    def _scrape_amazon(self, url: str) -> Dict[str, Any]:
        """Scrape Amazon product information"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            title = self._extract_amazon_title(soup)
            price_info = self._extract_amazon_price(soup)
            image_url = self._extract_amazon_image(soup)
            rating_info = self._extract_amazon_rating(soup)
            
            return {
                'title': title,
                'description': f'Amazon product: {title}',
                'category': self._guess_category(title),
                'merchant': 'amazon',
                'original_price': price_info.get('original_price'),
                'sale_price': price_info.get('sale_price'),
                'product_url': url,
                'image_url': image_url,
                'brand': self._extract_brand_from_title(title),
                'rating': rating_info.get('rating'),
                'rating_count': rating_info.get('rating_count'),
                'scraped': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping Amazon product: {e}")
            return self._create_fallback_product(url, 'amazon')
    
    def _scrape_home_depot(self, url: str) -> Dict[str, Any]:
        """Scrape Home Depot product information"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = self._extract_text_content(soup, [
                'h1[data-testid="product-header-title"]',
                'h1.product-title',
                'h1'
            ])
            
            price = self._extract_home_depot_price(soup)
            image_url = self._extract_home_depot_image(soup)
            
            return {
                'title': title,
                'description': f'Home Depot product: {title}',
                'category': self._guess_category(title),
                'merchant': 'home_depot',
                'original_price': price,
                'sale_price': None,
                'product_url': url,
                'image_url': image_url,
                'brand': self._extract_brand_from_title(title),
                'scraped': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping Home Depot product: {e}")
            return self._create_fallback_product(url, 'home_depot')
    
    def _scrape_lowes(self, url: str) -> Dict[str, Any]:
        """Scrape Lowes product information"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self._extract_text_content(soup, [
                'h1[data-testid="product-title"]',
                'h1.product-title',
                'h1'
            ])
            
            price = self._extract_lowes_price(soup)
            image_url = self._extract_lowes_image(soup)
            
            return {
                'title': title,
                'description': f'Lowes product: {title}',
                'category': self._guess_category(title),
                'merchant': 'lowes',
                'original_price': price,
                'sale_price': None,
                'product_url': url,
                'image_url': image_url,
                'brand': self._extract_brand_from_title(title),
                'scraped': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping Lowes product: {e}")
            return self._create_fallback_product(url, 'lowes')
    
    def _scrape_walmart(self, url: str) -> Dict[str, Any]:
        """Scrape Walmart product information"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self._extract_text_content(soup, [
                'h1[data-testid="product-title"]',
                'h1.product-title',
                'h1'
            ])
            
            price = self._extract_walmart_price(soup)
            image_url = self._extract_walmart_image(soup)
            
            return {
                'title': title,
                'description': f'Walmart product: {title}',
                'category': self._guess_category(title),
                'merchant': 'walmart',
                'original_price': price,
                'sale_price': None,
                'product_url': url,
                'image_url': image_url,
                'brand': self._extract_brand_from_title(title),
                'scraped': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping Walmart product: {e}")
            return self._create_fallback_product(url, 'walmart')
    
    def _scrape_generic(self, url: str) -> Dict[str, Any]:
        """Generic scraper for unknown websites"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract title from common selectors
            title = self._extract_text_content(soup, [
                'h1.product-title',
                'h1.title',
                'h1',
                'title'
            ])
            
            # Try to extract image
            image_url = self._extract_generic_image(soup)
            
            return {
                'title': title,
                'description': f'Product from {urlparse(url).netloc}: {title}',
                'category': self._guess_category(title),
                'merchant': 'other',
                'original_price': None,
                'sale_price': None,
                'product_url': url,
                'image_url': image_url,
                'brand': self._extract_brand_from_title(title),
                'scraped': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping generic product: {e}")
            return self._create_fallback_product(url, 'other')
    
    # Helper methods for Amazon
    def _extract_amazon_title(self, soup: BeautifulSoup) -> str:
        """Extract title from Amazon page"""
        selectors = [
            '#productTitle',
            'h1.a-size-large',
            'h1 span'
        ]
        return self._extract_text_content(soup, selectors)
    
    def _extract_amazon_price(self, soup: BeautifulSoup) -> Dict[str, Optional[float]]:
        """Extract price information from Amazon page"""
        price_info = {'original_price': None, 'sale_price': None}
        
        try:
            # Try different price selectors
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '.a-price-current .a-offscreen',
                '.a-price-symbol + .a-price-whole'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price:
                        price_info['sale_price'] = price
                        break
            
            # Look for original price if on sale
            original_price_element = soup.select_one('.a-text-price .a-offscreen')
            if original_price_element:
                original_price_text = original_price_element.get_text(strip=True)
                original_price = self._parse_price(original_price_text)
                if original_price:
                    price_info['original_price'] = original_price
                    
        except Exception as e:
            logger.debug(f"Error extracting Amazon price: {e}")
            
        return price_info
    
    def _extract_amazon_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main product image from Amazon page"""
        try:
            img_selectors = [
                '#landingImage',
                '.a-dynamic-image',
                '#ebooksImgBlkFront'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return img['src']
                    
        except Exception as e:
            logger.debug(f"Error extracting Amazon image: {e}")
            
        return None
    
    def _extract_amazon_rating(self, soup: BeautifulSoup) -> Dict[str, Optional[float]]:
        """Extract rating information from Amazon page"""
        rating_info = {'rating': None, 'rating_count': None}
        
        try:
            # Extract rating
            rating_element = soup.select_one('.a-icon-alt')
            if rating_element:
                rating_text = rating_element.get_text()
                rating_match = re.search(r'(\d+\.?\d*)\s*out\s*of', rating_text)
                if rating_match:
                    rating_info['rating'] = float(rating_match.group(1))
            
            # Extract rating count
            count_element = soup.select_one('#acrCustomerReviewText')
            if count_element:
                count_text = count_element.get_text()
                count_match = re.search(r'([\d,]+)', count_text)
                if count_match:
                    rating_info['rating_count'] = int(count_match.group(1).replace(',', ''))
                    
        except Exception as e:
            logger.debug(f"Error extracting Amazon rating: {e}")
            
        return rating_info
    
    # Helper methods for other sites
    def _extract_home_depot_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Home Depot page"""
        try:
            price_selectors = [
                '[data-testid="price-current"] .sr-only',
                '.price__current .u__screenreader',
                '.price-format__large-symbol + .price-format__main-price'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    return self._parse_price(price_text)
                    
        except Exception as e:
            logger.debug(f"Error extracting Home Depot price: {e}")
            
        return None
    
    def _extract_home_depot_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract image from Home Depot page"""
        try:
            img_selectors = [
                '.mediaBrowser__image img',
                '.product-image img',
                '.main-image img'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return img['src']
                    
        except Exception as e:
            logger.debug(f"Error extracting Home Depot image: {e}")
            
        return None
    
    def _extract_lowes_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Lowes page"""
        try:
            price_selectors = [
                '[data-testid="price-current"]',
                '.price-current',
                '.sr-only'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price:
                        return price
                        
        except Exception as e:
            logger.debug(f"Error extracting Lowes price: {e}")
            
        return None
    
    def _extract_lowes_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract image from Lowes page"""
        try:
            img_selectors = [
                '.primary-image img',
                '.product-image img',
                '.main-image img'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return img['src']
                    
        except Exception as e:
            logger.debug(f"Error extracting Lowes image: {e}")
            
        return None
    
    def _extract_walmart_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Walmart page"""
        try:
            price_selectors = [
                '[data-testid="price-current"]',
                '.price-current',
                '.visuallyhidden'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price = self._parse_price(price_text)
                    if price:
                        return price
                        
        except Exception as e:
            logger.debug(f"Error extracting Walmart price: {e}")
            
        return None
    
    def _extract_walmart_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract image from Walmart page"""
        try:
            img_selectors = [
                '.product-image img',
                '.main-image img',
                '[data-testid="hero-image"] img'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return img['src']
                    
        except Exception as e:
            logger.debug(f"Error extracting Walmart image: {e}")
            
        return None
    
    def _extract_generic_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract image from generic website"""
        try:
            img_selectors = [
                '.product-image img',
                '.main-image img',
                '.hero-image img',
                'img[alt*="product"]'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return img['src']
                    
        except Exception as e:
            logger.debug(f"Error extracting generic image: {e}")
            
        return None
    
    # Utility methods
    def _extract_text_content(self, soup: BeautifulSoup, selectors: list) -> str:
        """Extract text content using multiple selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 5:  # Ensure we have meaningful text
                    return text
        
        return "Product Title"
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text"""
        try:
            # Remove currency symbols and commas, extract numbers
            price_clean = re.sub(r'[^\d.]', '', price_text)
            if price_clean:
                return float(price_clean)
        except (ValueError, TypeError):
            pass
        return None
    
    def _extract_brand_from_title(self, title: str) -> Optional[str]:
        """Try to extract brand from product title"""
        # Common tool brands
        brands = [
            'DeWalt', 'DEWALT', 'Milwaukee', 'Makita', 'Bosch', 'Ryobi', 
            'BLACK+DECKER', 'Porter-Cable', 'Craftsman', 'Kobalt', 'Husky',
            'Stanley', 'Klein Tools', 'Fluke', 'Irwin', 'Channellock',
            'Kreg', 'Bessey', 'Festool', 'Ridgid', 'RIGID'
        ]
        
        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand
                
        # Try to extract first word as potential brand
        words = title.split()
        if words:
            return words[0]
            
        return None
    
    def _guess_category(self, title: str) -> str:
        """Guess product category from title"""
        title_lower = title.lower()
        
        tool_keywords = ['drill', 'saw', 'hammer', 'screwdriver', 'wrench', 'pliers', 'tool']
        material_keywords = ['wood', 'lumber', 'screw', 'nail', 'bolt', 'bracket', 'hinge']
        safety_keywords = ['safety', 'gloves', 'glasses', 'helmet', 'mask', 'protection']
        
        if any(keyword in title_lower for keyword in tool_keywords):
            return 'tools'
        elif any(keyword in title_lower for keyword in material_keywords):
            return 'materials'
        elif any(keyword in title_lower for keyword in safety_keywords):
            return 'safety'
        else:
            return 'other'
    
    def _create_fallback_product(self, url: str, merchant: str = 'other') -> Dict[str, Any]:
        """Create fallback product info when scraping fails"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        return {
            'title': f'Product from {domain}',
            'description': f'Product from {domain}. Please update the details manually.',
            'category': 'other',
            'merchant': merchant,
            'original_price': None,
            'sale_price': None,
            'product_url': url,
            'image_url': None,
            'brand': None,
            'rating': None,
            'rating_count': None,
            'scraped': False  # Indicates scraping failed
        }

# Create global instance
product_scraper = ProductScraper()