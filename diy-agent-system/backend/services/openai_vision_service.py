"""
OpenAI GPT-4 Vision Service for Image Analysis
"""
import os
import base64
import logging
from typing import Dict, List, Optional, Any
import openai
from openai import OpenAI
import json

logger = logging.getLogger(__name__)

class OpenAIVisionService:
    """Service for analyzing images using OpenAI GPT-4 Vision"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not found, vision features will use mock data")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI Vision service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    async def analyze_diy_project(self, image_base64: str, project_description: str = "") -> Dict[str, Any]:
        """
        Analyze DIY project image and extract information
        
        Args:
            image_base64: Base64 encoded image
            project_description: Optional description from user
            
        Returns:
            Dictionary containing project analysis
        """
        if not self.client:
            logger.info("Using mock data - OpenAI API not configured")
            return self._get_mock_diy_analysis()
        
        try:
            prompt = f"""
            Analyze this DIY project image and provide detailed information in JSON format.
            {f'User description: {project_description}' if project_description else ''}
            
            Please identify and return:
            {{
                "project_name": "descriptive name of the project",
                "project_type": "woodworking/electronics/crafts/metalworking/other",
                "description": "detailed description of what you see",
                "materials": [
                    {{
                        "name": "material name",
                        "specification": "size/type/grade",
                        "quantity": "estimated amount needed",
                        "estimated_price_range": "$X-Y"
                    }}
                ],
                "tools": [
                    {{
                        "name": "tool name",
                        "necessity": "Essential/Recommended/Optional"
                    }}
                ],
                "difficulty_level": "beginner/intermediate/advanced",
                "estimated_time": "X-Y hours/days",
                "safety_notes": ["safety consideration 1", "safety consideration 2"],
                "steps": ["step 1", "step 2", "..."]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Find JSON content between curly braces
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = result_text[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    logger.error("No JSON found in OpenAI response")
                    return self._get_mock_diy_analysis()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return self._get_mock_diy_analysis()
                
        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}")
            return self._get_mock_diy_analysis()
    
    async def identify_tool(self, image_base64: str) -> Dict[str, Any]:
        """
        Identify tool from image
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Dictionary containing tool identification
        """
        if not self.client:
            logger.info("Using mock data - OpenAI API not configured")
            return self._get_mock_tool_identification()
        
        try:
            prompt = """
            Identify this tool and provide detailed information in JSON format:
            {
                "tool_name": "specific name of the tool",
                "category": "power tool/hand tool/measuring/safety/other",
                "brand": "identified brand or 'Unknown'",
                "model": "model number if visible or 'Unknown'",
                "primary_use": "main purpose of this tool",
                "features": ["feature 1", "feature 2"],
                "condition": "new/good/fair/poor",
                "estimated_value": "$X-Y",
                "safety_rating": "1-5 based on proper safety features",
                "recommended_for": ["project type 1", "project type 2"],
                "alternatives": [
                    {
                        "name": "alternative tool name",
                        "reason": "why this is a good alternative"
                    }
                ]
            }
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content
            
            try:
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = result_text[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    logger.error("No JSON found in OpenAI response")
                    return self._get_mock_tool_identification()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return self._get_mock_tool_identification()
                
        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}")
            return self._get_mock_tool_identification()
    
    def _get_mock_diy_analysis(self) -> Dict[str, Any]:
        """Return mock DIY analysis data"""
        return {
            "project_name": "Custom Wooden Bookshelf",
            "project_type": "woodworking",
            "description": "A multi-tier wooden bookshelf project suitable for home organization",
            "materials": [
                {
                    "name": "Pine Wood Boards",
                    "specification": "1x12 inch, 8 feet long",
                    "quantity": "5 boards",
                    "estimated_price_range": "$75-100"
                },
                {
                    "name": "Wood Screws",
                    "specification": "2.5 inch drywall screws",
                    "quantity": "50 pieces",
                    "estimated_price_range": "$8-12"
                }
            ],
            "tools": [
                {
                    "name": "Circular Saw",
                    "necessity": "Essential"
                },
                {
                    "name": "Power Drill",
                    "necessity": "Essential"
                },
                {
                    "name": "Measuring Tape",
                    "necessity": "Essential"
                }
            ],
            "difficulty_level": "intermediate",
            "estimated_time": "4-6 hours",
            "safety_notes": [
                "Always wear safety glasses when cutting",
                "Use proper ventilation when sanding"
            ],
            "steps": [
                "Measure and mark cutting lines",
                "Cut boards to size",
                "Sand all surfaces",
                "Pre-drill screw holes",
                "Assemble frame",
                "Attach shelves",
                "Apply finish"
            ]
        }
    
    def _get_mock_tool_identification(self) -> Dict[str, Any]:
        """Return mock tool identification data"""
        return {
            "tool_name": "Cordless Drill",
            "category": "power tool",
            "brand": "DeWalt",
            "model": "DCD771C2",
            "primary_use": "Drilling holes and driving screws",
            "features": [
                "20V MAX Lithium-Ion battery",
                "Variable speed trigger",
                "LED work light"
            ],
            "condition": "good",
            "estimated_value": "$80-120",
            "safety_rating": 4,
            "recommended_for": [
                "Woodworking",
                "Home repairs",
                "Furniture assembly"
            ],
            "alternatives": [
                {
                    "name": "Impact Driver",
                    "reason": "Better for driving long screws"
                },
                {
                    "name": "Hammer Drill",
                    "reason": "Can drill into masonry"
                }
            ]
        }

# Singleton instance
vision_service = OpenAIVisionService()