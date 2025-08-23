"""
Product Models
Database models for storing recommended products with affiliate links
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from .base import Base


class ProductCategory(str, Enum):
    """Product categories"""
    POWER_TOOLS = "power_tools"
    HAND_TOOLS = "hand_tools"
    MEASURING = "measuring"
    FASTENING = "fastening"
    CUTTING = "cutting"
    SAFETY = "safety"
    MATERIALS = "materials"
    ADHESIVES = "adhesives"
    HARDWARE = "hardware"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    AUTOMOTIVE = "automotive"
    GARDEN = "garden"
    CRAFT = "craft"
    OTHER = "other"


class ProjectType(str, Enum):
    """Project types that products are suitable for"""
    WOODWORKING = "woodworking"
    ELECTRONICS = "electronics"
    AUTOMOTIVE = "automotive"
    HOME_IMPROVEMENT = "home_improvement"
    GARDENING = "gardening"
    CRAFTS = "crafts"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    GENERAL = "general"


class Retailer(str, Enum):
    """Supported retailers"""
    AMAZON = "amazon"
    HOME_DEPOT = "home_depot"
    LOWES = "lowes"
    WALMART = "walmart"
    OTHER = "other"


# Many-to-many table for product-project relationships
product_projects = Table(
    'product_projects',
    Base.metadata,
    Column('product_id', String, ForeignKey('products.id'), primary_key=True),
    Column('project_type', String, primary_key=True)
)


class Product(Base):
    """
    Product model for storing curated product recommendations with affiliate links
    """
    __tablename__ = "products"
    
    # Primary identification
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic product information
    title = Column(String(500), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(100))
    category = Column(String(50), nullable=False, index=True)  # ProductCategory enum
    description = Column(Text)
    features = Column(Text)  # JSON string of features list
    
    # Pricing information
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # For showing discounts
    currency = Column(String(3), default="USD")
    
    # Retailer and affiliate information
    retailer = Column(String(50), nullable=False)  # Retailer enum
    affiliate_link = Column(String(1000), nullable=False)
    product_url = Column(String(1000))  # Original product URL
    
    # Media
    image_url = Column(String(1000))
    additional_images = Column(Text)  # JSON string of additional image URLs
    
    # Quality and review information
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    quality_score = Column(Float)  # Internal quality assessment
    
    # Availability and stock
    in_stock = Column(Boolean, default=True)
    availability_status = Column(String(50), default="available")
    
    # Suitability and recommendations
    skill_level = Column(String(20))  # beginner, intermediate, advanced, professional
    budget_range = Column(String(20))  # under50, 50to150, etc.
    suitable_projects = Column(Text)  # JSON string of project types
    
    # SEO and search
    keywords = Column(Text)  # JSON string of search keywords
    tags = Column(Text)  # JSON string of tags
    
    # Admin and management
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    admin_notes = Column(Text)
    
    # Affiliate tracking
    affiliate_commission_rate = Column(Float)  # Percentage
    click_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_price_check = Column(DateTime)
    
    # Note: Removed relationship for now to fix SQLAlchemy error
    # project_types = relationship(
    #     "ProjectType",
    #     secondary=product_projects,
    #     back_populates="products"
    # )
    
    def __repr__(self):
        return f"<Product(id='{self.id}', title='{self.title}', brand='{self.brand}')>"
    
    @property
    def discount_percentage(self) -> float:
        """Calculate discount percentage if original price is available"""
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 1)
        return 0.0
    
    @property
    def is_on_sale(self) -> bool:
        """Check if product is currently on sale"""
        return self.original_price is not None and self.original_price > self.price
    
    @property
    def conversion_rate(self) -> float:
        """Calculate affiliate conversion rate"""
        if self.click_count > 0:
            return round((self.conversion_count / self.click_count) * 100, 2)
        return 0.0
    
    def to_dict(self):
        """Convert product to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "brand": self.brand,
            "model": self.model,
            "category": str(self.category) if self.category else "other",
            "description": self.description,
            "price": self.price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "retailer": str(self.retailer) if self.retailer else "other",
            "affiliate_link": self.affiliate_link,
            "image_url": self.image_url,
            "rating": self.rating,
            "review_count": self.review_count,
            "in_stock": self.in_stock,
            "is_featured": self.is_featured,
            "suitable_projects": self.suitable_projects,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProductAnalysis(Base):
    """
    Product analysis model for storing admin analysis results
    """
    __tablename__ = "product_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source information
    source_url = Column(String(1000), nullable=False)
    analysis_date = Column(DateTime, server_default=func.now())
    
    # Extracted information
    extracted_title = Column(String(500))
    extracted_brand = Column(String(100))
    extracted_price = Column(Float)
    extracted_description = Column(Text)
    extracted_features = Column(Text)  # JSON
    extracted_images = Column(Text)  # JSON array of image URLs
    extracted_rating = Column(Float)
    extracted_reviews = Column(Integer)
    
    # Analysis results
    quality_assessment = Column(Text)
    recommendation_score = Column(Float)
    category_prediction = Column(String(50))
    project_suitability = Column(Text)  # JSON
    
    # Admin decisions
    approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Product creation
    product_id = Column(String, ForeignKey('products.id'))
    product = relationship("Product", backref="analysis_history")
    
    # Metadata
    analysis_metadata = Column(Text)  # JSON with technical details
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProductAnalysis(id='{self.id}', url='{self.source_url}', approved={self.approved})>"


class AffiliateClick(Base):
    """
    Track affiliate link clicks for analytics
    """
    __tablename__ = "affiliate_clicks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Link information
    product_id = Column(String, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))  # Optional if user is logged in
    
    # Click details
    click_timestamp = Column(DateTime, server_default=func.now())
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # Support IPv6
    referrer = Column(String(1000))
    
    # Context
    page_source = Column(String(100))  # Which page the click came from
    session_id = Column(String(100))
    
    # Tracking
    converted = Column(Boolean, default=False)
    conversion_timestamp = Column(DateTime)
    commission_earned = Column(Float)
    
    # Relationships
    product = relationship("Product", backref="clicks")
    
    def __repr__(self):
        return f"<AffiliateClick(id='{self.id}', product_id='{self.product_id}', converted={self.converted})>"


class ProductRecommendationRule(Base):
    """
    Rules for automated product recommendations
    """
    __tablename__ = "recommendation_rules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Rule definition
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Conditions (stored as JSON)
    project_type_conditions = Column(Text)  # JSON
    budget_conditions = Column(Text)  # JSON
    skill_level_conditions = Column(Text)  # JSON
    category_conditions = Column(Text)  # JSON
    
    # Actions (stored as JSON)
    boost_products = Column(Text)  # JSON array of product IDs to boost
    exclude_products = Column(Text)  # JSON array of product IDs to exclude
    boost_categories = Column(Text)  # JSON array of categories to boost
    
    # Rule properties
    priority = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProductRecommendationRule(id='{self.id}', name='{self.name}', active={self.is_active})>"