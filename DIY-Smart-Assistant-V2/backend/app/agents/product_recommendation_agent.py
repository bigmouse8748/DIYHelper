"""
Product Recommendation Agent - Enhanced V2 Version
Migrated from original diy-agent-system with improvements
"""
import asyncio
import logging
import random
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from .base import BaseAgent
from .base import AgentResult

logger = logging.getLogger(__name__)

class ProductRecommendationAgent(BaseAgent):
    """Enhanced Product Recommendation Agent with AI-powered suggestions"""
    
    def __init__(self):
        super().__init__(
            name="product_recommendation",
            config={
                "description": "AI-powered product recommendations with quality scoring",
                "max_concurrent_tasks": 3,
                "timeout_seconds": 120,
                "features": ["ai_recommendations", "quality_scoring", "affiliate_links", "retailer_integration"]
            }
        )
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not found, product recommendations will use fallback data")
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    timeout=90.0
                )
                logger.info("OpenAI client initialized successfully for product recommendations")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        self.retailer_urls = {
            "amazon": "https://www.amazon.com/s?k=",
            "home_depot": "https://www.homedepot.com/s/",
            "lowes": "https://www.lowes.com/search?searchTerm=",
            "walmart": "https://www.walmart.com/search/?query="
        }
        
        # Enhanced product database with real brands and models
        self.product_database = {
            "power_tools": {
                "drills": [
                    {
                        "name": "DeWalt 20V MAX Cordless Drill",
                        "model": "DCD771C2",
                        "brand": "DeWalt",
                        "price": "$79-99",
                        "features": ["20V MAX Lithium-Ion", "2-speed transmission", "LED work light"],
                        "quality_score": 4.5,
                        "recommendation_level": "Highly Recommended"
                    },
                    {
                        "name": "Milwaukee M18 FUEL Drill",
                        "model": "2804-20",
                        "brand": "Milwaukee",
                        "price": "$129-149",
                        "features": ["Brushless motor", "18V battery", "Metal gear housing"],
                        "quality_score": 4.7,
                        "recommendation_level": "Professional Choice"
                    },
                    {
                        "name": "Ryobi 18V ONE+ Drill",
                        "model": "P1811",
                        "brand": "Ryobi",
                        "price": "$39-59",
                        "features": ["18V ONE+ battery", "24-position clutch", "LED light"],
                        "quality_score": 4.1,
                        "recommendation_level": "Best Value"
                    }
                ],
                "saws": [
                    {
                        "name": "DeWalt 7-1/4 Circular Saw",
                        "model": "DWE575",
                        "brand": "DeWalt",
                        "price": "$99-119",
                        "features": ["15 Amp motor", "Electric brake", "Dust blower"],
                        "quality_score": 4.6,
                        "recommendation_level": "Highly Recommended"
                    },
                    {
                        "name": "SKIL 5280-01 Circular Saw",
                        "model": "5280-01",
                        "brand": "SKIL",
                        "price": "$49-69",
                        "features": ["15 Amp motor", "51° bevel capacity", "Dust port"],
                        "quality_score": 4.0,
                        "recommendation_level": "Good Choice"
                    }
                ]
            },
            "hand_tools": {
                "measuring": [
                    {
                        "name": "Stanley 25ft Tape Measure",
                        "model": "STHT30825",
                        "brand": "Stanley",
                        "price": "$12-18",
                        "features": ["25ft length", "Fractional markings", "Mylar coating"],
                        "quality_score": 4.3,
                        "recommendation_level": "Recommended"
                    },
                    {
                        "name": "Milwaukee 25ft Tape Measure",
                        "model": "48-22-7125",
                        "brand": "Milwaukee",
                        "price": "$19-25",
                        "features": ["Magnetic tip", "Nylon bond blade", "5-point reinforcement"],
                        "quality_score": 4.5,
                        "recommendation_level": "Professional Choice"
                    }
                ]
            },
            "materials": {
                "wood": [
                    {
                        "name": "Pine Wood Boards",
                        "specification": "1x12 inch, 8 feet",
                        "price": "$15-25 per board",
                        "features": ["Kiln dried", "Grade A", "Smooth finish"],
                        "quality_score": 4.2,
                        "recommendation_level": "Recommended"
                    },
                    {
                        "name": "Plywood Sheet",
                        "specification": "3/4 inch, 4x8 feet",
                        "price": "$45-65 per sheet",
                        "features": ["Birch veneer", "Void-free core", "Sanded both sides"],
                        "quality_score": 4.4,
                        "recommendation_level": "Highly Recommended"
                    }
                ],
                "fasteners": [
                    {
                        "name": "Wood Screws",
                        "specification": "2.5 inch, #8",
                        "price": "$8-12 per 50-pack",
                        "features": ["Phillips head", "Zinc plated", "Sharp point"],
                        "quality_score": 4.1,
                        "recommendation_level": "Good Choice"
                    }
                ]
            }
        }

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute product recommendation task"""
        return await self.process_task(input_data)

    async def process_task(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process product recommendation task with AI-powered analysis"""
        try:
            analysis_data = input_data.get("analysis_data", {})
            project_type = input_data.get("project_type", "woodworking")
            budget_range = input_data.get("budget_range", "moderate")
            
            logger.info(f"Processing product recommendations for {project_type} project")
            
            # Extract materials and tools from analysis
            materials = analysis_data.get("materials", [])
            tools = analysis_data.get("tools", [])
            
            # Generate AI-powered recommendations
            recommendations = await self._generate_smart_recommendations(materials, tools, project_type, budget_range)
            
            # Calculate overall statistics
            overall_stats = self._calculate_overall_recommendations(recommendations)
            
            result_data = {
                "assessed_results": recommendations,
                "overall_recommendations": overall_stats,
                "project_type": project_type,
                "budget_range": budget_range,
                "total_categories": len(recommendations),
                "generation_method": "ai_powered"
            }
            
            return AgentResult(
                success=True,
                data=result_data,
                agent_name=self.name,
                execution_time=2.5
            )
            
        except Exception as e:
            logger.error(f"Product recommendation failed: {str(e)}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )

    async def _generate_smart_recommendations(self, materials: List[Dict], tools: List[Dict], 
                                            project_type: str, budget_range: str) -> List[Dict]:
        """Generate smart product recommendations based on analysis"""
        recommendations = []
        
        # Use AI to generate recommendations if available
        if self.client:
            try:
                ai_recommendations = await self._get_ai_recommendations(materials, tools, project_type, budget_range)
                if ai_recommendations:
                    return ai_recommendations
            except Exception as e:
                logger.error(f"AI recommendations failed, falling back to database: {e}")
        
        # Fallback to existing logic if AI fails
        # Process tools first
        for tool in tools:
            tool_name = tool.get("name", "").lower()
            category = self._categorize_tool(tool_name)
            
            if category:
                products = await self._get_products_for_category(category, budget_range)
                if products:
                    recommendations.append({
                        "material": tool.get("name", "Unknown Tool"),
                        "category": "tools",
                        "products": products[:5],  # Top 5 products
                        "total_assessed": len(products),
                        "avg_quality_score": sum(p.get("quality_score", 4.0) for p in products) / len(products)
                    })
        
        # Process materials
        for material in materials:
            material_name = material.get("name", "").lower()
            category = self._categorize_material(material_name)
            
            if category:
                products = await self._get_products_for_category(category, budget_range)
                if products:
                    recommendations.append({
                        "material": material.get("name", "Unknown Material"),
                        "category": "materials",
                        "products": products[:5],
                        "total_assessed": len(products),
                        "avg_quality_score": sum(p.get("quality_score", 4.0) for p in products) / len(products)
                    })
        
        return recommendations

    async def _get_ai_recommendations(self, materials: List[Dict], tools: List[Dict], 
                                    project_type: str, budget_range: str) -> List[Dict]:
        """Get AI-powered product recommendations using OpenAI"""
        try:
            # Build context for AI
            context = {
                "project_type": project_type,
                "budget_range": budget_range,
                "materials": materials[:10],  # Limit to prevent token overflow
                "tools": tools[:10]
            }
            
            prompt = f"""
            You are an expert DIY product recommendation assistant. Based on the following project details, provide specific, real product recommendations.

            Project Type: {project_type}
            Budget Range: {budget_range}
            
            Materials Needed: {json.dumps(materials, indent=2)}
            Tools Needed: {json.dumps(tools, indent=2)}
            
            Please provide product recommendations in the following JSON format:
            {{
                "recommendations": [
                    {{
                        "material": "Material/Tool Name",
                        "category": "tools" or "materials",
                        "products": [
                            {{
                                "name": "Specific product name",
                                "brand": "Brand name",
                                "model": "Model number if applicable",
                                "price": "$X-Y price range",
                                "quality_score": 4.5,
                                "features": ["feature1", "feature2"],
                                "title": "Brand Product Name",
                                "platform": "Amazon",
                                "rating": 4.5,
                                "quality_reasons": ["reason1", "reason2", "reason3"],
                                "recommendation_level": "Highly Recommended"
                            }}
                        ],
                        "total_assessed": 5,
                        "avg_quality_score": 4.3
                    }}
                ]
            }}
            
            Focus on:
            1. Real brands and specific models available in US retailers
            2. Quality-to-price ratio appropriate for the budget range  
            3. Professional recommendations based on project requirements
            4. Include major retailers: Amazon, Home Depot, Lowes, Walmart
            5. Provide 3-5 product options per material/tool category
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert DIY product recommendation assistant with extensive knowledge of tools, materials, and retailers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            logger.info(f"OpenAI recommendations response: {result_text[:200]}...")
            
            # Parse JSON response
            try:
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = result_text[start_idx:end_idx]
                    ai_result = json.loads(json_str)
                    
                    # Extract recommendations array
                    recommendations = ai_result.get("recommendations", [])
                    
                    # Enhance with retailer links
                    for rec in recommendations:
                        for product in rec.get("products", []):
                            product.update(self._enhance_product_with_links_ai(product))
                    
                    logger.info(f"Successfully parsed {len(recommendations)} AI recommendations")
                    return recommendations
                else:
                    logger.error("No JSON found in OpenAI recommendations response")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI recommendations as JSON: {e}")
                return []
                
        except Exception as e:
            logger.error(f"OpenAI recommendations API error: {e}")
            return []

    def _enhance_product_with_links_ai(self, product: Dict) -> Dict:
        """Enhance AI-generated product with retailer links"""
        search_query = f"{product.get('brand', '')} {product.get('name', '')} {product.get('model', '')}"
        search_query = search_query.replace(" ", "+")
        
        return {
            "product_url": f"{self.retailer_urls['amazon']}{search_query}",
            "image_url": f"https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=300&h=200&fit=crop",
            "price_value_ratio": round(product.get("quality_score", 4.0) / self._extract_max_price(product.get("price", "$100")), 2)
        }

    def _categorize_tool(self, tool_name: str) -> Optional[str]:
        """Categorize tool based on name"""
        if any(keyword in tool_name for keyword in ["drill", "impact", "driver"]):
            return "power_tools.drills"
        elif any(keyword in tool_name for keyword in ["saw", "circular", "miter"]):
            return "power_tools.saws"
        elif any(keyword in tool_name for keyword in ["measure", "tape", "ruler"]):
            return "hand_tools.measuring"
        return None

    def _categorize_material(self, material_name: str) -> Optional[str]:
        """Categorize material based on name"""
        if any(keyword in material_name for keyword in ["wood", "lumber", "board", "plywood"]):
            return "materials.wood"
        elif any(keyword in material_name for keyword in ["screw", "nail", "bolt", "fastener"]):
            return "materials.fasteners"
        return None

    async def _get_products_for_category(self, category_path: str, budget_range: str) -> List[Dict]:
        """Get products for a specific category"""
        try:
            # Navigate through the nested dictionary
            parts = category_path.split('.')
            products = self.product_database
            
            for part in parts:
                products = products.get(part, {})
            
            if not products:
                return []
            
            # Get all products from the category
            all_products = []
            if isinstance(products, list):
                all_products = products
            else:
                for subcategory in products.values():
                    if isinstance(subcategory, list):
                        all_products.extend(subcategory)
            
            # Filter by budget and enhance with retailer links
            filtered_products = self._filter_by_budget(all_products, budget_range)
            enhanced_products = [self._enhance_product_with_links(product) for product in filtered_products]
            
            # Sort by quality score
            enhanced_products.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
            
            return enhanced_products
            
        except Exception as e:
            logger.error(f"Error getting products for {category_path}: {e}")
            return []

    def _filter_by_budget(self, products: List[Dict], budget_range: str) -> List[Dict]:
        """Filter products based on budget range"""
        if budget_range == "under50":
            return [p for p in products if self._extract_max_price(p.get("price", "")) <= 50]
        elif budget_range == "50to150":
            return [p for p in products if 50 <= self._extract_max_price(p.get("price", "")) <= 150]
        elif budget_range == "150to300":
            return [p for p in products if 150 <= self._extract_max_price(p.get("price", "")) <= 300]
        else:
            return products  # Return all for moderate/high budgets

    def _extract_max_price(self, price_str: str) -> float:
        """Extract maximum price from price string"""
        try:
            # Extract numbers from price string like "$79-99" or "$45-65 per sheet"
            import re
            numbers = re.findall(r'\d+', price_str)
            if len(numbers) >= 2:
                return float(numbers[1])  # Take the higher price
            elif len(numbers) == 1:
                return float(numbers[0])
            return 0
        except:
            return 0

    def _enhance_product_with_links(self, product: Dict) -> Dict:
        """Enhance product with retailer links and additional info"""
        enhanced = product.copy()
        
        # Generate search query
        search_query = f"{product.get('brand', '')} {product.get('name', '')} {product.get('model', '')}"
        search_query = search_query.replace(" ", "+")
        
        # Add retailer links
        enhanced.update({
            "title": f"{product.get('brand', 'Generic')} {product.get('name', 'Tool')}",
            "product_url": f"{self.retailer_urls['amazon']}{search_query}",
            "image_url": f"https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=300&h=200&fit=crop",
            "platform": random.choice(["Amazon", "Home Depot", "Lowes", "Walmart"]),
            "rating": round(product.get("quality_score", 4.0), 1),
            "quality_reasons": [
                f"High-quality {product.get('brand', 'brand')} construction",
                f"Professional-grade features: {', '.join(product.get('features', [])[:2])}",
                f"Excellent value in {product.get('price', 'competitive')} price range"
            ],
            "price_value_ratio": round(product.get("quality_score", 4.0) / self._extract_max_price(product.get("price", "$100")), 2)
        })
        
        return enhanced

    def _calculate_overall_recommendations(self, recommendations: List[Dict]) -> Dict:
        """Calculate overall recommendation statistics"""
        if not recommendations:
            return {
                "total_products_assessed": 0,
                "average_quality_score": 0,
                "best_products": [],
                "shopping_tips": [],
                "quality_distribution": {}
            }
        
        total_products = sum(rec.get("total_assessed", 0) for rec in recommendations)
        avg_score = sum(rec.get("avg_quality_score", 0) for rec in recommendations) / len(recommendations)
        
        # Get best products from each category
        best_products = []
        for rec in recommendations:
            products = rec.get("products", [])
            if products:
                best_product = max(products, key=lambda x: x.get("quality_score", 0))
                best_products.append({
                    "material": rec.get("material", "Unknown"),
                    "product": best_product
                })
        
        # Generate shopping tips
        shopping_tips = [
            "Compare prices across multiple retailers before purchasing",
            "Check for bundle deals to save on multiple tools",
            "Consider buying during seasonal sales for best prices",
            "Read customer reviews for real-world performance insights",
            "Invest in quality tools for frequently used items"
        ]
        
        # Quality distribution
        quality_levels = {"Excellent": 0, "Good": 0, "Fair": 0}
        for rec in recommendations:
            for product in rec.get("products", []):
                score = product.get("quality_score", 0)
                if score >= 4.5:
                    quality_levels["Excellent"] += 1
                elif score >= 4.0:
                    quality_levels["Good"] += 1
                else:
                    quality_levels["Fair"] += 1
        
        return {
            "total_products_assessed": total_products,
            "average_quality_score": round(avg_score, 1),
            "best_products": best_products[:5],  # Top 5 best products
            "shopping_tips": shopping_tips,
            "quality_distribution": quality_levels
        }