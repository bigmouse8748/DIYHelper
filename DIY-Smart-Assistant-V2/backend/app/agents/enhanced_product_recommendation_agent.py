"""
Enhanced Product Recommendation Agent - V2 with Original System Logic
Comprehensive integration of the original system's detailed recommendation engine
"""
import asyncio
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class EnhancedProductRecommendationAgent(BaseAgent):
    """Complete Product Recommendation Agent with original system's detailed logic"""
    
    def __init__(self):
        super().__init__(
            name="enhanced_product_recommendation", 
            config={
                "description": "Comprehensive AI-powered product recommendations with detailed analysis",
                "features": ["intelligent_matching", "budget_optimization", "quality_scoring", "retailer_integration"]
            }
        )
        
        # Enhanced product database from original system with comprehensive coverage
        self.recommendations_db = {
            "Power Drill": [
                {
                    "brand": "DeWalt",
                    "model": "DCD771C2 20V MAX Cordless Drill",
                    "level": "professional",
                    "price_range": "$89-129",
                    "features": ["Brushless motor", "Long battery life", "Professional grade"],
                    "specifications": "20V MAX Lithium-Ion, 2-speed transmission, LED light"
                },
                {
                    "brand": "BLACK+DECKER",
                    "model": "LD120VA 20V MAX Cordless Drill",
                    "level": "entry",
                    "price_range": "$45-65",
                    "features": ["Good for beginners", "Affordable", "Reliable"],
                    "specifications": "20V MAX Lithium-Ion, single speed, compact design"
                },
                {
                    "brand": "Milwaukee",
                    "model": "M18 FUEL 2804-20",
                    "level": "professional",
                    "price_range": "$149-199",
                    "features": ["High torque", "FUEL technology", "Long runtime"],
                    "specifications": "M18 FUEL brushless motor, REDLINK PLUS intelligence"
                }
            ],
            "Circular Saw": [
                {
                    "brand": "SKILSAW",
                    "model": "SPT67WL-01 15-Amp 7-1/4 In. Sidewinder",
                    "level": "professional", 
                    "price_range": "$179-229",
                    "features": ["Magnesium construction", "Lightweight", "Professional grade"],
                    "specifications": "15-Amp motor, 24-tooth carbide blade, magnesium shoe"
                },
                {
                    "brand": "BLACK+DECKER",
                    "model": "BDECS300C 13-Amp 7-1/4-Inch Circular Saw",
                    "level": "entry",
                    "price_range": "$69-89",
                    "features": ["Entry level", "Good value", "Reliable performance"],
                    "specifications": "13-Amp motor, laser guide, bevel capacity 0-45°"
                }
            ],
            "Table Saw": [
                {
                    "brand": "SawStop",
                    "model": "PCS175-TGP236 1.75-HP Professional Cabinet Saw",
                    "level": "professional",
                    "price_range": "$2,199-2,799",
                    "features": ["Safety brake technology", "Professional grade", "Precise cuts"],
                    "specifications": "1.75-HP motor, 36-inch fence, SawStop safety system"
                },
                {
                    "brand": "DeWalt",
                    "model": "DWE7491RS 10-Inch Jobsite Table Saw",
                    "level": "intermediate",
                    "price_range": "$649-799",
                    "features": ["Portable", "Rolling stand", "Rack and pinion fence"],
                    "specifications": "15-Amp motor, 32.5-inch rip capacity, rolling stand"
                }
            ],
            "Safety Glasses": [
                {
                    "brand": "3M",
                    "model": "SecureFit 400 Series SF401AF",
                    "level": "professional",
                    "price_range": "$8-15",
                    "features": ["Anti-fog coating", "ANSI Z87.1 certified", "Comfortable fit"],
                    "specifications": "Anti-fog lens, pressure diffusion temple technology"
                }
            ]
        }
        
        # Material recommendations database
        self.material_recommendations = {
            "Pine Wood Board": [
                {
                    "brand": "Select Pine",
                    "model": "Construction Grade Pine Board 3/4\" x 12\" x 8'",
                    "level": "standard",
                    "price_range": "$25-45",
                    "features": ["Good quality", "Standard grade", "Widely available"],
                    "specifications": "Kiln-dried, construction grade, smooth surface"
                }
            ],
            "Wood Screws": [
                {
                    "brand": "GRK Fasteners",
                    "model": "R4 Multi-Purpose Wood Screws",
                    "level": "professional",
                    "price_range": "$15-25",
                    "features": ["Self-drilling", "Premium quality", "Strong grip"],
                    "specifications": "Washer head, deep thread, corrosion resistant"
                }
            ],
            "Wood Glue": [
                {
                    "brand": "Titebond",
                    "model": "Titebond III Ultimate Wood Glue",
                    "level": "professional",
                    "price_range": "$8-15",
                    "features": ["Waterproof", "Strong bond", "FDA approved"],
                    "specifications": "100% waterproof, 24-hour cure time, sandable"
                }
            ]
        }
        
        # US retailer URLs for real shopping links
        self.retailers = [
            {
                "name": "Home Depot",
                "search_url": "https://www.homedepot.com/s/{}",
                "domain": "homedepot.com"
            },
            {
                "name": "Lowes", 
                "search_url": "https://www.lowes.com/search?searchTerm={}",
                "domain": "lowes.com"
            },
            {
                "name": "Amazon",
                "search_url": "https://www.amazon.com/s?k={}",
                "domain": "amazon.com"
            },
            {
                "name": "Walmart",
                "search_url": "https://www.walmart.com/search/?query={}",
                "domain": "walmart.com"
            }
        ]
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute comprehensive product recommendation analysis"""
        try:
            analysis_data = input_data.get("analysis_data", {})
            project_type = input_data.get("project_type", "woodworking")
            budget_range = input_data.get("budget_range", "medium")
            
            # Extract tools and materials from analysis data
            tools_and_materials = []
            
            # Add tools from analysis
            tools = analysis_data.get("tools", [])
            for tool in tools:
                tools_and_materials.append({
                    "name": tool.get("name", ""),
                    "type": "tool",
                    "necessity": tool.get("necessity", "recommended"),
                    "specifications": tool.get("specifications", "")
                })
            
            # Add materials from analysis
            materials = analysis_data.get("materials", [])
            for material in materials:
                tools_and_materials.append({
                    "name": material.get("name", ""),
                    "type": "material",
                    "quantity": material.get("quantity", ""),
                    "specifications": material.get("specification", "")
                })
            
            logger.info(f"Processing {len(tools_and_materials)} items for recommendations")
            
            # Generate comprehensive recommendations
            recommendations = []
            for item in tools_and_materials:
                item_name = item.get("name", "")
                item_type = item.get("type", "tool")
                
                # Get AI-powered recommendations
                ai_recommendations = await self._get_ai_recommendations(
                    item_name, item_type, project_type, budget_range
                )
                
                # Convert to products with shopping links
                products = await self._search_products(ai_recommendations, item_name)
                
                if products:
                    recommendations.append({
                        "material": item_name,
                        "category": item_type,
                        "products": products,
                        "total_assessed": len(products),
                        "avg_quality_score": sum(p.get("quality_score", 4.0) for p in products) / len(products) if products else 4.0
                    })
            
            # Generate overall recommendations summary
            overall_recommendations = self._generate_overall_recommendations(recommendations)
            
            result_data = {
                "assessed_results": recommendations,
                "overall_recommendations": overall_recommendations,
                "recommendation_method": "enhanced_ai_matching",
                "total_categories": len(recommendations),
                "budget_optimization": True
            }
            
            return AgentResult(
                success=True,
                data=result_data,
                execution_time=2.5,
                metadata={"items_processed": len(tools_and_materials)}
            )
            
        except Exception as e:
            logger.error(f"Enhanced product recommendation error: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                error=f"Product recommendation failed: {str(e)}"
            )
    
    async def _get_ai_recommendations(self, item_name: str, item_type: str, project_type: str, budget_level: str) -> List[Dict]:
        """Enhanced AI recommendation logic from original system"""
        
        # Get base recommendations from database
        if item_type == "tool":
            base_recommendations = self.recommendations_db.get(item_name, [])
        else:
            base_recommendations = self.material_recommendations.get(item_name, [])
            
        # If no exact match, use intelligent matching
        if not base_recommendations:
            base_recommendations = await self._generate_generic_recommendations(item_name, item_type, project_type)
            
        # Apply AI-powered filtering and prioritization
        enhanced_recommendations = []
        for rec in base_recommendations:
            rec = rec.copy()  # Avoid modifying original data
            
            # AI priority scoring based on budget level
            if budget_level in ["under50", "50to150"]:
                if rec["level"] == "entry":
                    rec["ai_priority"] = 0.9
                elif rec["level"] == "intermediate": 
                    rec["ai_priority"] = 0.7
                else:
                    rec["ai_priority"] = 0.3
            elif budget_level in ["150to300", "300to500"]:
                if rec["level"] == "intermediate":
                    rec["ai_priority"] = 0.9
                elif rec["level"] == "professional":
                    rec["ai_priority"] = 0.8
                else:
                    rec["ai_priority"] = 0.6
            else:  # over500 or not specified
                if rec["level"] == "professional":
                    rec["ai_priority"] = 0.9
                else:
                    rec["ai_priority"] = 0.7
            
            # Project type optimization
            if project_type == "woodworking" and any(word in item_name.lower() for word in ["drill", "saw", "wood", "clamp"]):
                rec["ai_priority"] *= 1.2
            elif project_type == "electronics" and any(word in item_name.lower() for word in ["safety", "wire", "solder"]):
                rec["ai_priority"] *= 1.1
                
            enhanced_recommendations.append(rec)
            
        # Sort by AI priority
        enhanced_recommendations.sort(key=lambda x: x.get("ai_priority", 0.5), reverse=True)
        
        # Ensure we have exactly 3 recommendations
        while len(enhanced_recommendations) < 3:
            additional_recs = await self._generate_additional_recommendations(
                item_name, item_type, project_type, budget_level, 3 - len(enhanced_recommendations)
            )
            enhanced_recommendations.extend(additional_recs)
        
        return enhanced_recommendations[:3]
    
    async def _generate_generic_recommendations(self, item_name: str, item_type: str, project_type: str) -> List[Dict]:
        """Generate recommendations for items not in database"""
        generic_recommendations = []
        
        # Smart keyword matching for tools
        tool_brands = {
            "drill": [
                {"brand": "DeWalt", "model": f"{item_name} - Professional Series", "level": "professional", "price_range": "$89-149"},
                {"brand": "BLACK+DECKER", "model": f"{item_name} - Home Series", "level": "entry", "price_range": "$39-69"},
                {"brand": "Milwaukee", "model": f"{item_name} - M18 FUEL", "level": "professional", "price_range": "$129-199"}
            ],
            "saw": [
                {"brand": "SKILSAW", "model": f"{item_name} - Professional", "level": "professional", "price_range": "$159-249"},
                {"brand": "BLACK+DECKER", "model": f"{item_name} - Compact", "level": "entry", "price_range": "$69-99"},
                {"brand": "DeWalt", "model": f"{item_name} - FlexVolt", "level": "intermediate", "price_range": "$119-179"}
            ],
            "hammer": [
                {"brand": "Stanley", "model": f"{item_name} - FatMax", "level": "professional", "price_range": "$25-45"},
                {"brand": "Estwing", "model": f"{item_name} - Steel Handle", "level": "intermediate", "price_range": "$35-55"},
                {"brand": "Craftsman", "model": f"{item_name} - Classic", "level": "entry", "price_range": "$15-25"}
            ]
        }
        
        # Material brand mapping
        material_brands = {
            "wood": [
                {"brand": "Select Pine", "model": f"{item_name} - Construction Grade", "level": "standard", "price_range": "$15-35"},
                {"brand": "Premium Oak", "model": f"{item_name} - Hardwood", "level": "professional", "price_range": "$45-85"},
                {"brand": "Plywood", "model": f"{item_name} - Multi-ply", "level": "intermediate", "price_range": "$25-55"}
            ],
            "screw": [
                {"brand": "GRK Fasteners", "model": f"{item_name} - Multi-Purpose", "level": "professional", "price_range": "$12-25"},
                {"brand": "Spax", "model": f"{item_name} - PowerLag", "level": "intermediate", "price_range": "$8-18"},
                {"brand": "Deck Mate", "model": f"{item_name} - Standard", "level": "entry", "price_range": "$5-12"}
            ]
        }
        
        # Intelligent keyword matching
        database = tool_brands if item_type == "tool" else material_brands
        for keyword, recommendations in database.items():
            if keyword.lower() in item_name.lower():
                return recommendations[:3]
        
        # Default fallback recommendations
        default_brands = ["Stanley", "Craftsman", "Kobalt"] if item_type == "tool" else ["Generic Brand", "Home Depot", "Lowes"]
        for i, brand in enumerate(default_brands):
            level = ["entry", "intermediate", "professional"][i]
            price_ranges = ["$10-25", "$20-40", "$35-60"]
            generic_recommendations.append({
                "brand": brand,
                "model": f"{item_name} - {level.title()} Grade",
                "level": level,
                "price_range": price_ranges[i],
                "features": [f"Good for {project_type}", "Reliable quality", "Available in US stores"]
            })
        
        return generic_recommendations
    
    async def _generate_additional_recommendations(self, item_name: str, item_type: str, project_type: str, budget_level: str, count_needed: int) -> List[Dict]:
        """Generate additional recommendations to reach target count"""
        additional_recs = []
        
        backup_brands = {
            "tool": ["Ridgid", "Ryobi", "Porter-Cable", "Bosch", "Makita"],
            "material": ["Simpson Strong-Tie", "Titebond", "3M", "Gorilla", "Loctite"]
        }
        
        brands = backup_brands.get(item_type, ["Generic Brand"])
        levels = ["entry", "intermediate", "professional"]
        
        for i in range(count_needed):
            brand = brands[i % len(brands)]
            level = levels[i % len(levels)]
            
            price_ranges = {
                "entry": ["$8-20", "$15-30", "$25-45"],
                "intermediate": ["$20-40", "$35-60", "$50-80"],
                "professional": ["$40-80", "$70-120", "$100-180"]
            }
            
            additional_recs.append({
                "brand": brand,
                "model": f"{item_name} - {level.title()} Series",
                "level": level,
                "price_range": price_ranges[level][i % 3],
                "features": [f"Suitable for {project_type}", "Good value", "US retailer available"],
                "ai_priority": 0.4 - (i * 0.1)
            })
        
        return additional_recs
    
    async def _search_products(self, ai_recommendations: List[Dict], item_name: str) -> List[Dict]:
        """Convert AI recommendations to product listings with shopping links"""
        products = []
        
        for i, recommendation in enumerate(ai_recommendations):
            retailer = self.retailers[i % len(self.retailers)]
            
            # Build search term
            brand = recommendation['brand'].replace(" ", "+")
            model_key = recommendation['model'].split(" - ")[0] if " - " in recommendation['model'] else recommendation['model']
            search_term = f"{brand}+{model_key}".replace(" ", "+")
            
            # Generate shopping URL
            direct_url = retailer['search_url'].format(search_term)
            
            # Extract price 
            price_range = recommendation['price_range']
            price = price_range.split('-')[0].strip() if '-' in price_range else price_range
            if not price.startswith('$'):
                price = f"${price}"
            
            product = {
                "title": f"{recommendation['brand']} {recommendation['model']}",
                "description": f"Level: {recommendation['level'].title()} | Features: {', '.join(recommendation.get('features', [])[:2])}",
                "price": price.replace('$', '').replace(',', ''),  # Numeric for frontend
                "image_url": self._get_relevant_product_image(recommendation, retailer['name']),
                "product_url": direct_url,
                "platform": retailer['name'],
                "rating": self._calculate_rating(recommendation),
                "quality_score": self._calculate_quality_score(recommendation),
                "quality_reasons": recommendation.get('features', [f"Good {recommendation['level']} choice", "Reliable brand", "Available online"])[:3],
                "price_value_ratio": self._calculate_value_ratio(recommendation),
                "recommendation_level": self._get_recommendation_level(recommendation['level']),
                "specifications": recommendation.get('specifications', 'Standard specifications')
            }
            
            products.append(product)
        
        return products
    
    def _get_relevant_product_image(self, recommendation: Dict, retailer_name: str) -> str:
        """Get relevant product image based on type and brand"""
        brand = recommendation.get('brand', '').lower()
        model = recommendation.get('model', '').lower()
        
        # Tool type specific images
        tool_images = {
            'drill': "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop",
            'saw': "https://images.unsplash.com/photo-1609592067508-0e2120ac7fe7?w=400&h=300&fit=crop",
            'hammer': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
            'safety': "https://images.unsplash.com/photo-1577962917302-cd874c99b6d3?w=400&h=300&fit=crop",
            'screw': "https://images.unsplash.com/photo-1609592067508-0e2120ac7fe7?w=400&h=300&fit=crop",
            'wood': "https://images.unsplash.com/photo-1541123437800-1bb1317badc2?w=400&h=300&fit=crop",
            'glue': "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400&h=300&fit=crop"
        }
        
        # Brand specific images
        brand_images = {
            'dewalt': "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop",
            'black+decker': "https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=400&h=300&fit=crop",
            'milwaukee': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
        }
        
        # Check brand first
        if brand in brand_images:
            return brand_images[brand]
            
        # Then check tool type
        for tool_type, image_url in tool_images.items():
            if tool_type in model or tool_type in brand:
                return image_url
        
        # Default image
        return "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop"
    
    def _calculate_rating(self, recommendation: Dict) -> float:
        """Calculate product rating based on level"""
        level_ratings = {
            "professional": 4.6,
            "intermediate": 4.3,
            "entry": 4.0,
            "standard": 4.2
        }
        return level_ratings.get(recommendation['level'], 4.0)
    
    def _calculate_quality_score(self, recommendation: Dict) -> float:
        """Calculate quality score"""
        level_scores = {
            "professional": 4.8,
            "intermediate": 4.4,
            "entry": 4.0,
            "standard": 4.2
        }
        return level_scores.get(recommendation['level'], 4.0)
    
    def _calculate_value_ratio(self, recommendation: Dict) -> float:
        """Calculate price-to-value ratio"""
        level_values = {
            "professional": 4.2,
            "intermediate": 4.5,
            "entry": 4.7,
            "standard": 4.3
        }
        return level_values.get(recommendation['level'], 4.0)
    
    def _get_recommendation_level(self, level: str) -> str:
        """Get recommendation level label"""
        level_labels = {
            "professional": "Professional Choice",
            "intermediate": "Highly Recommended", 
            "entry": "Best Value",
            "standard": "Good Choice"
        }
        return level_labels.get(level, "Recommended")
    
    def _generate_overall_recommendations(self, recommendations: List[Dict]) -> Dict:
        """Generate comprehensive overall recommendations"""
        total_products = sum(rec['total_assessed'] for rec in recommendations)
        avg_score = sum(rec['avg_quality_score'] for rec in recommendations) / len(recommendations) if recommendations else 4.0
        
        # Get best products
        best_products = []
        for rec in recommendations[:3]:  # Top 3 categories
            if rec['products']:
                best_product = max(rec['products'], key=lambda p: p['quality_score'])
                best_products.append({
                    "material": rec['material'],
                    "product": {
                        "title": best_product['title'],
                        "platform": best_product['platform'],
                        "product_url": best_product['product_url'],
                        "price": best_product['price'],
                        "quality_score": best_product['quality_score']
                    }
                })
        
        return {
            "total_products_assessed": total_products,
            "average_quality_score": round(avg_score, 1),
            "best_products": best_products,
            "shopping_tips": [
                "Choose products with 4.0+ star ratings for best quality",
                "Compare prices across multiple retailers (Home Depot, Lowes, Amazon, Walmart)", 
                "Read recent customer reviews for real-world performance insights",
                "Consider your skill level when choosing between entry-level and professional tools",
                "Look for bundle deals when buying multiple tools from the same brand",
                "Check for manufacturer warranties and return policies",
                "Buy safety equipment first - never compromise on safety gear",
                "Consider renting expensive tools for one-time projects"
            ],
            "quality_distribution": {
                "Professional Choice": sum(1 for rec in recommendations for p in rec['products'] if p['recommendation_level'] == 'Professional Choice'),
                "Highly Recommended": sum(1 for rec in recommendations for p in rec['products'] if p['recommendation_level'] == 'Highly Recommended'),
                "Best Value": sum(1 for rec in recommendations for p in rec['products'] if p['recommendation_level'] == 'Best Value'),
                "Good Choice": sum(1 for rec in recommendations for p in rec['products'] if p['recommendation_level'] == 'Good Choice')
            },
            "budget_breakdown": {
                "estimated_total": f"${sum(int(p['price']) for rec in recommendations for p in rec['products'] if p['price'].isdigit())}-{sum(int(p['price']) * 1.3 for rec in recommendations for p in rec['products'] if p['price'].isdigit()):.0f}",
                "cost_optimization_tips": [
                    "Start with essential tools only",
                    "Consider buying used for expensive items",
                    "Look for seasonal sales and clearance events"
                ]
            }
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input has analysis data"""
        analysis_data = input_data.get("analysis_data")
        return analysis_data is not None and isinstance(analysis_data, dict)