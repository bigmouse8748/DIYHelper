"""
Product recommendation database models
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from models.user_models import Base

class ProductCategory(str, Enum):
    TOOLS = "tools"
    MATERIALS = "materials"
    SAFETY = "safety"
    ACCESSORIES = "accessories"
    OTHER = "other"

class ProductMerchant(str, Enum):
    AMAZON = "amazon"
    HOME_DEPOT = "home_depot"
    LOWES = "lowes"
    WALMART = "walmart"
    OTHER = "other"

class ProductRecommendation(Base):
    __tablename__ = "product_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(ProductCategory), default=ProductCategory.OTHER)
    merchant = Column(SQLEnum(ProductMerchant), default=ProductMerchant.OTHER)
    
    # Product details
    original_price = Column(Float, nullable=True)
    sale_price = Column(Float, nullable=True)
    discount_percentage = Column(Integer, nullable=True)
    
    # Links and images
    product_url = Column(String(1000), nullable=False)  # Affiliate link
    image_url = Column(String(1000), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    
    # Display settings
    is_featured = Column(Boolean, default=False)  # Featured products show first
    is_active = Column(Boolean, default=True)  # Active products are displayed
    sort_order = Column(Integer, default=0)  # For custom ordering
    
    # SEO and metadata
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    rating = Column(Float, nullable=True)  # Product rating (1-5)
    rating_count = Column(Integer, nullable=True)  # Number of ratings
    
    # DIY project types this product is suitable for
    project_types = Column(JSON, nullable=True)  # Array of project types like ["woodworking", "general"]
    
    # Admin information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # Admin user ID who created this
    
    # Analytics (for future use)
    click_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value if self.category else None,
            'merchant': self.merchant.value if self.merchant else None,
            'original_price': self.original_price,
            'sale_price': self.sale_price,
            'discount_percentage': self.discount_percentage,
            'product_url': self.product_url,
            'image_url': self.image_url,
            'thumbnail_url': self.thumbnail_url,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'brand': self.brand,
            'model': self.model,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'click_count': self.click_count,
            'view_count': self.view_count,
            'project_types': self.project_types or []
        }
    
    def get_display_price(self):
        """Get the price to display (sale price if available, otherwise original price)"""
        return self.sale_price if self.sale_price else self.original_price
    
    def has_discount(self):
        """Check if product has a discount"""
        return self.sale_price and self.original_price and self.sale_price < self.original_price
    
    def calculate_discount_percentage(self):
        """Calculate discount percentage"""
        if self.has_discount():
            return int(((self.original_price - self.sale_price) / self.original_price) * 100)
        return 0