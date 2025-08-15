"""
Product recommendation service for database operations
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.product_models import ProductRecommendation, ProductCategory, ProductMerchant
from database import get_db_session
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProductService:
    """Service for product recommendation database operations"""
    
    @staticmethod
    def create_product(
        title: str,
        product_url: str,
        description: Optional[str] = None,
        category: str = "other",
        merchant: Optional[str] = None,
        original_price: Optional[float] = None,
        sale_price: Optional[float] = None,
        image_url: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        rating: Optional[float] = None,
        rating_count: Optional[int] = None,
        is_featured: bool = False,
        project_types: Optional[List[str]] = None,
        created_by: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new product recommendation"""
        try:
            with get_db_session() as db:
                # Auto-detect merchant from URL if not provided
                if not merchant:
                    merchant = ProductService._detect_merchant_from_url(product_url)
                
                # Auto-generate thumbnail from image if needed
                thumbnail_url = ProductService._generate_thumbnail_url(image_url) if image_url else None
                
                # Calculate discount percentage if both prices provided
                discount_percentage = None
                if original_price and sale_price and sale_price < original_price:
                    discount_percentage = int(((original_price - sale_price) / original_price) * 100)
                
                # Ensure title is never None or empty
                if not title or title.strip() == '':
                    # Create fallback title based on URL
                    parsed = urlparse(product_url)
                    domain = parsed.netloc.replace('www.', '')
                    title = f"Product from {domain}"
                
                new_product = ProductRecommendation(
                    title=title,
                    description=description,
                    category=ProductCategory(category),
                    merchant=ProductMerchant(merchant),
                    original_price=original_price,
                    sale_price=sale_price,
                    discount_percentage=discount_percentage,
                    product_url=product_url,
                    image_url=image_url,
                    thumbnail_url=thumbnail_url,
                    brand=brand,
                    model=model,
                    rating=rating,
                    rating_count=rating_count,
                    is_featured=is_featured,
                    project_types=project_types or [],
                    created_by=created_by,
                    created_at=datetime.utcnow()
                )
                
                db.add(new_product)
                db.commit()
                db.refresh(new_product)
                
                logger.info(f"Product created successfully: {title}")
                return new_product.to_dict()
                
        except IntegrityError as e:
            logger.error(f"Product creation failed due to integrity constraint: {e}")
            return None
        except Exception as e:
            logger.error(f"Product creation failed: {e}")
            return None
    
    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            with get_db_session() as db:
                product = db.query(ProductRecommendation).filter(
                    ProductRecommendation.id == product_id
                ).first()
                return product.to_dict() if product else None
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            return None
    
    @staticmethod
    def get_all_products(
        include_inactive: bool = False,
        category: Optional[str] = None,
        merchant: Optional[str] = None,
        project_type: Optional[str] = None,
        featured_only: bool = False,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all products with optional filters"""
        try:
            with get_db_session() as db:
                query = db.query(ProductRecommendation)
                
                # Filter by active status
                if not include_inactive:
                    query = query.filter(ProductRecommendation.is_active == True)
                
                # Filter by category
                if category:
                    query = query.filter(ProductRecommendation.category == ProductCategory(category))
                
                # Filter by merchant
                if merchant:
                    query = query.filter(ProductRecommendation.merchant == ProductMerchant(merchant))
                
                # Filter by project type  
                if project_type:
                    # For SQLite compatibility, use LIKE to search within JSON array
                    query = query.filter(ProductRecommendation.project_types.like(f'%"{project_type}"%'))
                
                # Filter by search term (search in title, description, brand, model)
                if search:
                    search_term = f'%{search.strip()}%'
                    query = query.filter(
                        ProductRecommendation.title.like(search_term) |
                        ProductRecommendation.description.like(search_term) |
                        ProductRecommendation.brand.like(search_term) |
                        ProductRecommendation.model.like(search_term)
                    )
                
                # Filter by featured
                if featured_only:
                    query = query.filter(ProductRecommendation.is_featured == True)
                
                # Order by featured first, then by sort_order, then by created_at desc
                query = query.order_by(
                    ProductRecommendation.is_featured.desc(),
                    ProductRecommendation.sort_order.asc(),
                    ProductRecommendation.created_at.desc()
                )
                
                products = query.all()
                return [product.to_dict() for product in products]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []
    
    @staticmethod
    def update_product(
        product_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        merchant: Optional[str] = None,
        original_price: Optional[float] = None,
        sale_price: Optional[float] = None,
        product_url: Optional[str] = None,
        image_url: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        rating: Optional[float] = None,
        rating_count: Optional[int] = None,
        is_featured: Optional[bool] = None,
        is_active: Optional[bool] = None,
        sort_order: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a product recommendation"""
        try:
            with get_db_session() as db:
                product = db.query(ProductRecommendation).filter(
                    ProductRecommendation.id == product_id
                ).first()
                
                if not product:
                    return None
                
                # Update fields if provided
                if title is not None:
                    product.title = title
                if description is not None:
                    product.description = description
                if category is not None:
                    product.category = ProductCategory(category)
                if merchant is not None:
                    product.merchant = ProductMerchant(merchant)
                if original_price is not None:
                    product.original_price = original_price
                if sale_price is not None:
                    product.sale_price = sale_price
                if product_url is not None:
                    product.product_url = product_url
                if image_url is not None:
                    product.image_url = image_url
                    product.thumbnail_url = ProductService._generate_thumbnail_url(image_url)
                if brand is not None:
                    product.brand = brand
                if model is not None:
                    product.model = model
                if rating is not None:
                    product.rating = rating
                if rating_count is not None:
                    product.rating_count = rating_count
                if is_featured is not None:
                    product.is_featured = is_featured
                if is_active is not None:
                    product.is_active = is_active
                if sort_order is not None:
                    product.sort_order = sort_order
                
                # Recalculate discount percentage
                if product.original_price and product.sale_price and product.sale_price < product.original_price:
                    product.discount_percentage = int(((product.original_price - product.sale_price) / product.original_price) * 100)
                else:
                    product.discount_percentage = None
                
                product.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(product)
                
                logger.info(f"Product updated successfully: {product.title}")
                return product.to_dict()
                
        except Exception as e:
            logger.error(f"Product update failed: {e}")
            return None
    
    @staticmethod
    def delete_product(product_id: int) -> bool:
        """Delete a product recommendation"""
        try:
            with get_db_session() as db:
                product = db.query(ProductRecommendation).filter(
                    ProductRecommendation.id == product_id
                ).first()
                
                if product:
                    db.delete(product)
                    db.commit()
                    logger.info(f"Product deleted successfully: {product.title}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Product deletion failed: {e}")
            return False
    
    @staticmethod
    def increment_click_count(product_id: int) -> bool:
        """Increment click count for analytics"""
        try:
            with get_db_session() as db:
                product = db.query(ProductRecommendation).filter(
                    ProductRecommendation.id == product_id
                ).first()
                
                if product:
                    product.click_count += 1
                    db.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to increment click count: {e}")
            return False
    
    @staticmethod
    def increment_view_count(product_id: int) -> bool:
        """Increment view count for analytics"""
        try:
            with get_db_session() as db:
                product = db.query(ProductRecommendation).filter(
                    ProductRecommendation.id == product_id
                ).first()
                
                if product:
                    product.view_count += 1
                    db.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to increment view count: {e}")
            return False
    
    @staticmethod
    def _detect_merchant_from_url(url: str) -> str:
        """Auto-detect merchant from URL"""
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc
            
            if 'amazon.com' in domain or 'amzn.to' in domain:
                return 'amazon'
            elif 'homedepot.com' in domain:
                return 'home_depot'
            elif 'lowes.com' in domain:
                return 'lowes'
            elif 'walmart.com' in domain:
                return 'walmart'
            else:
                return 'other'
        except:
            return 'other'
    
    @staticmethod
    def _generate_thumbnail_url(image_url: str) -> Optional[str]:
        """Generate thumbnail URL from image URL"""
        # For now, just return the same URL
        # In a production app, you might want to generate actual thumbnails
        return image_url
    
    @staticmethod
    def get_categories() -> List[Dict[str, str]]:
        """Get all available product categories"""
        return [
            {"value": category.value, "label": category.value.replace('_', ' ').title()} 
            for category in ProductCategory
        ]
    
    @staticmethod
    def get_merchants() -> List[Dict[str, str]]:
        """Get all available merchants"""
        return [
            {"value": merchant.value, "label": merchant.value.replace('_', ' ').title()} 
            for merchant in ProductMerchant
        ]