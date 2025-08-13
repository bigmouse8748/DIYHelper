"""
Tool identification and price tracking models
"""
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ToolIdentification(Base):
    __tablename__ = "tool_identifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    category = Column(String, nullable=True)  # power_tool, hand_tool, measuring, etc.
    confidence_score = Column(Float, default=0.0)
    identified_at = Column(DateTime, default=datetime.utcnow)
    
    # JSON fields for complex data
    specifications = Column(JSON, nullable=True)  # {"voltage": "20V", "rpm": "1500"}
    price_data = Column(JSON, nullable=True)  # {"amazon": 149.99, "home_depot": 159.99}
    shopping_links = Column(JSON, nullable=True)  # {"amazon": "url", "home_depot": "url"}
    product_images = Column(JSON, nullable=True)  # {"amazon": "img_url", "home_depot": "img_url"}
    alternatives = Column(JSON, nullable=True)  # [{"brand": "Milwaukee", "model": "...", "price": ...}]
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="identification", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "brand": self.brand,
            "model": self.model,
            "category": self.category,
            "confidence_score": self.confidence_score,
            "identified_at": self.identified_at.isoformat() if self.identified_at else None,
            "specifications": self.specifications,
            "price_data": self.price_data,
            "shopping_links": self.shopping_links,
            "product_images": self.product_images,
            "alternatives": self.alternatives
        }

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_identification_id = Column(Integer, ForeignKey("tool_identifications.id"), nullable=False)
    retailer = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    tracked_at = Column(DateTime, default=datetime.utcnow)
    in_stock = Column(Boolean, default=True)
    sale_price = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    
    # Relationship
    identification = relationship("ToolIdentification", back_populates="price_history")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "retailer": self.retailer,
            "price": self.price,
            "currency": self.currency,
            "tracked_at": self.tracked_at.isoformat() if self.tracked_at else None,
            "in_stock": self.in_stock,
            "sale_price": self.sale_price,
            "original_price": self.original_price
        }