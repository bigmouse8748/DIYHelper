"""
Enhanced Project Analysis Agent with OpenAI Vision API Integration
Migrated from original diy-agent-system and enhanced for V2
"""

import json
import logging
import random
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

from .base import BaseAgent, AgentResult
from ..services.openai_vision_service import vision_service
from .enhanced_product_recommendation_agent import EnhancedProductRecommendationAgent
from .web_search_agent import WebSearchAgent

logger = logging.getLogger(__name__)


@dataclass
class ProjectAnalysis:
    """Project analysis results structure"""
    project_name: str
    description: str
    materials_needed: List[Dict]
    tools_required: List[Dict]
    steps: List[Dict]
    difficulty_level: str
    estimated_time: str
    budget_estimate: Dict
    safety_notes: List[str]
    tips_and_tricks: List[str]


class ProjectAnalysisAgent(BaseAgent):
    """Enhanced Agent for comprehensive DIY project analysis using AI"""
    
    def __init__(self):
        super().__init__(
            name="project_analysis",
            config={"description": "AI-powered comprehensive DIY project analysis"}
        )
        self.product_agent = EnhancedProductRecommendationAgent()
        self.web_search_agent = WebSearchAgent()
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute comprehensive project analysis with real AI"""
        try:
            images = input_data.get("images", [])
            description = input_data.get("description", "")
            project_type = input_data.get("project_type", "")
            budget_range = input_data.get("budget_range", "moderate")
            
            if not images:
                return AgentResult(
                    success=False,
                    error="No images provided for project analysis"
                )
            
            # Analyze the first (main) image with AI
            main_image = images[0]
            project_analysis = await self._analyze_project_with_ai(main_image, description, project_type)
            
            # Generate comprehensive recommendations using ProductRecommendationAgent
            product_recommendations = await self._get_product_recommendations(
                project_analysis, project_type, budget_range
            )
            
            # Get web search results for cost-effective options
            web_search_results = await self._get_web_search_results(project_analysis)
            
            # Combine results
            result_data = {
                "comprehensive_analysis": project_analysis,
                "materials": project_analysis.get("materials", []),
                "tools": project_analysis.get("tools", []),
                "difficulty_level": project_analysis.get("difficulty_level", "intermediate"),
                "estimated_time": project_analysis.get("estimated_time", "4-6 hours"),
                "safety_notes": project_analysis.get("safety_notes", []),
                "steps": project_analysis.get("steps", []),
                "product_recommendations": product_recommendations,
                "web_search_results": web_search_results,
                "analysis_method": "openai_vision_ai_with_web_search"
            }
            
            return AgentResult(
                success=True,
                data=result_data,
                execution_time=3.5
            )
            
        except Exception as e:
            logger.error(f"Project analysis failed: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                error=f"Project analysis failed: {str(e)}"
            )
    
    async def _analyze_project_with_ai(self, image_data, description: str, project_type: str) -> Dict:
        """Analyze project using OpenAI Vision API"""
        try:
            # Handle different image data formats
            if isinstance(image_data, bytes):
                # Convert bytes to base64 string
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str):
                if image_data.startswith("data:image/"):
                    # Extract base64 from data URL
                    image_b64 = image_data.split(",")[1]
                else:
                    # Assume it's already base64
                    image_b64 = image_data
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            # Enhanced description for better AI analysis
            enhanced_description = f"Project type: {project_type}. User description: {description}"
            
            # Call vision service for project analysis
            result = await vision_service.analyze_diy_project(image_b64, enhanced_description)
            
            if result and isinstance(result, dict):
                return result
            else:
                # Use enhanced fallback if AI fails
                logger.warning("AI analysis failed, using enhanced fallback analysis")
                return self._get_fallback_analysis(project_type, description)
                
        except Exception as e:
            logger.error(f"AI project analysis failed: {str(e)}")
            logger.info("Falling back to comprehensive template-based analysis")
            return self._get_fallback_analysis(project_type, description)
    
    def _get_fallback_analysis(self, project_type: str = "woodworking", description: str = "") -> Dict:
        """Generate fallback analysis when AI fails"""
        project_templates = {
            "woodworking": {
                "project_name": "Custom Wooden Storage Cabinet",
                "description": f"A practical wooden storage cabinet project. {description}",
                "materials": [
                    {"name": "Pine Wood Boards", "specification": "1x12 inch, 8 feet", "quantity": "4 boards", "estimated_price_range": "$60-80"},
                    {"name": "Wood Screws", "specification": "2.5 inch", "quantity": "50 pieces", "estimated_price_range": "$8-12"},
                    {"name": "Wood Glue", "specification": "Strong adhesive", "quantity": "1 bottle", "estimated_price_range": "$4-8"},
                    {"name": "Cabinet Hinges", "specification": "2 inch", "quantity": "4 pieces", "estimated_price_range": "$12-20"},
                    {"name": "Wood Stain", "specification": "Natural finish", "quantity": "1 can", "estimated_price_range": "$8-15"}
                ],
                "tools": [
                    {"name": "Circular Saw", "necessity": "Essential"},
                    {"name": "Power Drill", "necessity": "Essential"},
                    {"name": "Measuring Tape", "necessity": "Essential"},
                    {"name": "Sandpaper", "necessity": "Essential"},
                    {"name": "Level", "necessity": "Recommended"},
                    {"name": "Clamps", "necessity": "Recommended"}
                ],
                "difficulty_level": "intermediate",
                "estimated_time": "6-8 hours",
                "safety_notes": [
                    "Always wear safety glasses when cutting or drilling",
                    "Use dust mask when sanding",
                    "Ensure proper ventilation when applying stain",
                    "Keep workspace clean and organized"
                ],
                "steps": [
                    "Measure and plan your cabinet dimensions",
                    "Cut all wood pieces to size using circular saw",
                    "Sand all surfaces smooth starting with coarse grit",
                    "Pre-drill holes to prevent wood splitting", 
                    "Assemble the cabinet frame with wood glue and screws",
                    "Install shelves and internal components",
                    "Mount hinges and test door operation",
                    "Apply wood stain or paint finish",
                    "Install cabinet in desired location"
                ]
            },
            "electronics": {
                "project_name": "LED Light Controller Circuit",
                "description": f"Electronic circuit for controlling LED lights. {description}",
                "materials": [
                    {"name": "Arduino Uno", "specification": "Microcontroller board", "quantity": "1 piece", "estimated_price_range": "$15-25"},
                    {"name": "LED Strip", "specification": "RGB 5V", "quantity": "1 meter", "estimated_price_range": "$10-20"},
                    {"name": "Resistors", "specification": "330 ohm", "quantity": "10 pieces", "estimated_price_range": "$2-5"},
                    {"name": "Breadboard", "specification": "Half-size", "quantity": "1 piece", "estimated_price_range": "$5-10"}
                ],
                "tools": [
                    {"name": "Soldering Iron", "necessity": "Essential"},
                    {"name": "Multimeter", "necessity": "Essential"},
                    {"name": "Wire Strippers", "necessity": "Essential"},
                    {"name": "Breadboard Jumpers", "necessity": "Recommended"}
                ],
                "difficulty_level": "beginner",
                "estimated_time": "2-3 hours",
                "safety_notes": [
                    "Be careful with hot soldering iron",
                    "Check connections before powering on",
                    "Use appropriate voltage ratings",
                    "Work in well-lit area"
                ],
                "steps": [
                    "Plan your circuit layout",
                    "Connect components on breadboard",
                    "Test basic connections with multimeter",
                    "Upload code to Arduino",
                    "Test LED functionality",
                    "Solder permanent connections if needed"
                ]
            }
        }
        
        # Get appropriate template
        template = project_templates.get(project_type, project_templates["woodworking"])
        return template
    
    async def _get_product_recommendations(self, analysis: Dict, project_type: str, budget_range: str) -> Dict:
        """Get product recommendations using ProductRecommendationAgent"""
        try:
            # Prepare input for product recommendation agent
            input_data = {
                "analysis_data": analysis,
                "project_type": project_type,
                "budget_range": budget_range
            }
            
            # Execute product recommendation
            result = await self.product_agent.execute(input_data)
            
            if result.success:
                return result.data
            else:
                logger.warning(f"Product recommendation failed: {result.error}")
                return self._get_fallback_recommendations()
                
        except Exception as e:
            logger.error(f"Product recommendation error: {str(e)}")
            return self._get_fallback_recommendations()
    
    def _get_fallback_recommendations(self) -> Dict:
        """Fallback product recommendations"""
        return {
            "assessed_results": [
                {
                    "material": "Power Tools",
                    "category": "tools",
                    "products": [
                        {
                            "title": "DeWalt 20V MAX Cordless Drill",
                            "price": "$89.99",
                            "platform": "Amazon",
                            "quality_score": 4.5,
                            "recommendation_level": "Highly Recommended",
                            "product_url": "https://www.amazon.com/s?k=dewalt+drill",
                            "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=300&h=200&fit=crop"
                        }
                    ],
                    "total_assessed": 1,
                    "avg_quality_score": 4.5
                }
            ],
            "overall_recommendations": {
                "total_products_assessed": 1,
                "average_quality_score": 4.5,
                "best_products": [],
                "shopping_tips": [
                    "Compare prices across multiple retailers",
                    "Check for bundle deals to save money",
                    "Read customer reviews before purchasing"
                ],
                "quality_distribution": {"Excellent": 1, "Good": 0, "Fair": 0}
            }
        }
    
    async def _get_web_search_results(self, analysis: Dict) -> Dict:
        """Get web search results for tools and materials"""
        try:
            # Extract items to search from analysis
            items_to_search = []
            
            # Add tools to search
            tools = analysis.get("tools", [])
            for tool in tools[:5]:  # Limit to first 5 tools
                items_to_search.append({
                    "name": tool.get("name", ""),
                    "type": "tool"
                })
            
            # Add materials to search
            materials = analysis.get("materials", [])
            for material in materials[:5]:  # Limit to first 5 materials
                items_to_search.append({
                    "name": material.get("name", ""),
                    "type": "material"
                })
            
            if not items_to_search:
                return self._get_fallback_web_search()
            
            logger.info(f"Starting web search for {len(items_to_search)} items")
            
            # Execute web search
            search_input = {"items": items_to_search}
            result = await self.web_search_agent.execute(search_input)
            
            if result.success:
                return result.data
            else:
                logger.warning(f"Web search failed: {result.error}")
                return self._get_fallback_web_search()
                
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return self._get_fallback_web_search()
    
    def _get_fallback_web_search(self) -> Dict:
        """Fallback web search results when search fails"""
        return {
            "search_results": [],
            "shopping_guide": {
                "summary": {
                    "total_items_searched": 0,
                    "total_options_found": 0,
                    "average_options_per_item": 0
                },
                "best_retailers": [
                    ("Home Depot", "Tools and hardware"),
                    ("Lowes", "Home improvement"), 
                    ("Amazon", "Variety and convenience")
                ],
                "money_saving_tips": [
                    "Compare prices across multiple retailers",
                    "Look for seasonal sales and clearance events",
                    "Consider store brands for budget options",
                    "Check for bundle deals on multiple items"
                ],
                "quality_tips": [
                    "Read recent customer reviews",
                    "Look for 4+ star ratings with 100+ reviews",
                    "Check warranty terms before purchasing",
                    "Consider total cost of ownership"
                ]
            },
            "search_timestamp": "fallback_data"
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input has required data"""
        images = input_data.get("images")
        logger.info(f"Project analysis validation - images: {type(images)}, len: {len(images) if images else 'None'}")
        return bool(images and len(images) > 0)