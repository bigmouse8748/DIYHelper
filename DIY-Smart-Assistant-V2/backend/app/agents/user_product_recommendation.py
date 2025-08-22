"""
User Product Recommendation Agent
Provides product recommendations to users based on their project requirements
from pre-analyzed and stored product database with affiliate links
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

from .base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class ProductRecommendation:
    """Product recommendation structure for users"""
    id: str
    title: str
    brand: str
    category: str
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    affiliate_link: str = ""
    image_url: str = ""
    rating: float = 0.0
    review_count: int = 0
    in_stock: bool = True
    retailer: str = ""
    features: List[str] = None
    suitable_for: List[str] = None  # project types this product is suitable for
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "brand": self.brand,
            "category": self.category,
            "price": self.price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "affiliate_link": self.affiliate_link,
            "image_url": self.image_url,
            "rating": self.rating,
            "review_count": self.review_count,
            "in_stock": self.in_stock,
            "retailer": self.retailer,
            "features": self.features or [],
            "suitable_for": self.suitable_for or []
        }


class UserProductRecommendationAgent(BaseAgent):
    """Agent for providing product recommendations to users"""
    
    def __init__(self):
        super().__init__(
            name="user_product_recommendation",
            config={"description": "Provides product recommendations to users with affiliate links"}
        )
        
        # Project type mappings
        self.project_categories = {
            "woodworking": ["power_tools", "hand_tools", "measuring", "fastening", "safety"],
            "electronics": ["tools", "components", "measuring", "safety"],
            "automotive": ["automotive_tools", "power_tools", "safety"],
            "home_improvement": ["power_tools", "hand_tools", "measuring", "fastening", "safety"],
            "gardening": ["garden_tools", "outdoor", "safety"],
            "crafts": ["craft_tools", "adhesives", "measuring"],
            "plumbing": ["plumbing_tools", "fastening", "measuring"],
            "electrical": ["electrical_tools", "measuring", "safety"]
        }
        
        # Budget ranges
        self.budget_ranges = {
            "under50": (0, 50),
            "50to150": (50, 150),
            "150to300": (150, 300),
            "300to500": (300, 500),
            "over500": (500, float('inf'))
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute user product recommendation"""
        try:
            # Extract user requirements
            project_type = input_data.get("project_type", "general")
            budget_range = input_data.get("budget_range", "50to150")
            skill_level = input_data.get("skill_level", "intermediate")
            specific_needs = input_data.get("specific_needs", [])
            user_preferences = input_data.get("user_preferences", {})
            
            # Get product recommendations
            recommendations = await self._get_recommendations(
                project_type, budget_range, skill_level, specific_needs, user_preferences
            )
            
            # Get shopping tips and advice
            shopping_tips = await self._get_shopping_tips(project_type, budget_range, skill_level)
            
            # Calculate summary statistics
            total_products = len(recommendations)
            avg_rating = sum(r.rating for r in recommendations) / total_products if total_products > 0 else 0
            total_savings = sum(
                (r.original_price or r.price) - r.price 
                for r in recommendations 
                if r.original_price
            )
            
            return AgentResult(
                success=True,
                data={
                    "recommendations": [rec.to_dict() for rec in recommendations],
                    "project_type": project_type,
                    "budget_range": budget_range,
                    "skill_level": skill_level,
                    "summary": {
                        "total_products": total_products,
                        "average_rating": round(avg_rating, 1),
                        "total_savings": round(total_savings, 2),
                        "budget_min": self.budget_ranges.get(budget_range, (0, 0))[0],
                        "budget_max": self.budget_ranges.get(budget_range, (0, 0))[1]
                    },
                    "shopping_tips": shopping_tips,
                    "categories_covered": list(set(r.category for r in recommendations))
                },
                metadata={
                    "recommendation_source": "curated_affiliate_database",
                    "personalized": True
                }
            )
            
        except Exception as e:
            logger.error(f"User product recommendation failed: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                error=f"Product recommendation failed: {str(e)}"
            )
    
    async def _get_recommendations(
        self, 
        project_type: str, 
        budget_range: str, 
        skill_level: str,
        specific_needs: List[str],
        user_preferences: Dict
    ) -> List[ProductRecommendation]:
        """Get product recommendations based on user requirements"""
        
        # TODO: Replace with actual database queries
        # This will query the products database created by admin using the admin_product_analysis_agent
        
        # Simulate database lookup
        await asyncio.sleep(0.3)
        
        # Get budget constraints
        min_price, max_price = self.budget_ranges.get(budget_range, (0, 500))
        
        # Mock recommendations based on project type and budget
        mock_recommendations = []
        
        if project_type in ["woodworking", "home_improvement"]:
            # Power tools recommendations
            if max_price >= 100:
                mock_recommendations.append(ProductRecommendation(
                    id="drill_001",
                    title="DeWalt 20V MAX Cordless Drill Kit",
                    brand="DeWalt",
                    category="power_tools",
                    price=129.99,
                    original_price=149.99,
                    discount_percentage=13.3,
                    affiliate_link="https://amzn.to/3DIYDrill001",
                    image_url="https://images.unsplash.com/photo-1504148455328-c376907d081c?w=300&h=200&fit=crop",
                    rating=4.7,
                    review_count=2340,
                    retailer="Amazon",
                    features=["20V MAX battery", "LED light", "2-speed gearbox", "1/2'' chuck"],
                    suitable_for=["woodworking", "home_improvement", "general"]
                ))
            
            if max_price >= 80:
                mock_recommendations.append(ProductRecommendation(
                    id="saw_001",
                    title="BLACK+DECKER 20V MAX Circular Saw",
                    brand="BLACK+DECKER",
                    category="power_tools",
                    price=79.99,
                    original_price=99.99,
                    discount_percentage=20.0,
                    affiliate_link="https://homedepot.com/affiliate/saw001",
                    image_url="https://images.unsplash.com/photo-1609504231852-84edfdd89b25?w=300&h=200&fit=crop",
                    rating=4.3,
                    review_count=890,
                    retailer="Home Depot",
                    features=["6.5'' blade", "20V battery", "Lightweight design"],
                    suitable_for=["woodworking", "home_improvement"]
                ))
        
        if project_type in ["electronics", "general"]:
            mock_recommendations.append(ProductRecommendation(
                id="multimeter_001",
                title="Fluke 87V Digital Multimeter",
                brand="Fluke",
                category="measuring",
                price=299.99,
                affiliate_link="https://amzn.to/3ElectroMeter",
                image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300&h=200&fit=crop",
                rating=4.9,
                review_count=567,
                retailer="Amazon",
                features=["True RMS", "Temperature measurement", "Min/Max recording"],
                suitable_for=["electronics", "automotive", "general"]
            ))
        
        # Add safety equipment (always recommended)
        if min_price <= 25:
            mock_recommendations.append(ProductRecommendation(
                id="safety_001",
                title="3M Safety Glasses with Anti-Fog Coating",
                brand="3M",
                category="safety",
                price=24.99,
                original_price=29.99,
                discount_percentage=16.7,
                affiliate_link="https://amzn.to/3SafetyFirst",
                image_url="https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=300&h=200&fit=crop",
                rating=4.6,
                review_count=1450,
                retailer="Amazon",
                features=["Anti-fog coating", "UV protection", "Comfortable fit"],
                suitable_for=["all_projects"]
            ))
        
        # Filter by budget
        filtered_recommendations = [
            rec for rec in mock_recommendations 
            if min_price <= rec.price <= max_price
        ]
        
        # Sort by rating and value
        filtered_recommendations.sort(key=lambda x: (x.rating, -x.price), reverse=True)
        
        return filtered_recommendations[:8]  # Return top 8 recommendations
    
    async def _get_shopping_tips(self, project_type: str, budget_range: str, skill_level: str) -> List[str]:
        """Get personalized shopping tips"""
        tips = []
        
        # Budget-based tips
        if budget_range in ["under50", "50to150"]:
            tips.extend([
                "Look for combo kits to get better value for your money",
                "Check for seasonal sales and clearance items",
                "Consider buying refurbished tools from reputable sellers"
            ])
        elif budget_range in ["300to500", "over500"]:
            tips.extend([
                "Invest in professional-grade tools for long-term value",
                "Look for tools with extended warranties",
                "Compare prices across multiple retailers for best deals"
            ])
        
        # Skill level tips
        if skill_level == "beginner":
            tips.extend([
                "Start with essential tools and expand your collection gradually",
                "Read product reviews from other beginners",
                "Consider tools with safety features and guides"
            ])
        elif skill_level == "professional":
            tips.extend([
                "Focus on tools that will increase your productivity",
                "Look for professional-grade durability and precision",
                "Consider tools that integrate with your existing equipment"
            ])
        
        # Project-specific tips
        if project_type == "woodworking":
            tips.append("Measure twice, cut once - invest in quality measuring tools")
        elif project_type == "electronics":
            tips.append("Precision is key - don't compromise on measuring instruments")
        
        # General tips
        tips.extend([
            "All links include our affiliate partnership for your support",
            "Prices and availability may vary - check retailer for latest info",
            "Always prioritize safety equipment in your purchases"
        ])
        
        return tips[:6]  # Return top 6 tips
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input has required project information"""
        required_fields = ["project_type"]
        return all(field in input_data for field in required_fields)