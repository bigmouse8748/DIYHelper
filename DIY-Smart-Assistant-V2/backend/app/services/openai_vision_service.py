"""
OpenAI GPT-4 Vision Service for Image Analysis - V2 Enhanced
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
                self.client = OpenAI(
                    api_key=api_key,
                    timeout=90.0  # 90 second timeout for OpenAI API calls
                )
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
                    ai_result = json.loads(json_str)
                    # Enhance AI result with detailed data
                    return self._enhance_ai_result(ai_result, project_description)
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
                "category": "power_tools/hand_tools/measuring/cutting/fastening/safety",
                "brand": "identified brand or 'Unknown'",
                "model": "model number if visible or 'Unknown'",
                "primary_use": "main purpose of this tool",
                "features": ["feature 1", "feature 2"],
                "condition": "new/good/fair/poor",
                "estimated_value": "$X-Y",
                "confidence": 0.95,
                "specifications": {
                    "key_specs": "relevant specifications"
                },
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
    
    def _enhance_ai_result(self, ai_result: Dict[str, Any], project_description: str) -> Dict[str, Any]:
        """Enhance AI result with detailed template data for comprehensive analysis"""
        try:
            # Get project type for template matching
            project_type = ai_result.get("project_type", "woodworking")
            
            # Get the enhanced template for this project type
            enhanced_template = self._get_enhanced_template(project_type, project_description)
            
            # Merge AI result with enhanced template
            enhanced_result = enhanced_template.copy()
            
            # Preserve AI-generated content where available
            if ai_result.get("project_name"):
                enhanced_result["project_name"] = ai_result["project_name"]
            if ai_result.get("description"):
                enhanced_result["description"] = f"{ai_result['description']}. {enhanced_template['description']}"
            if ai_result.get("difficulty_level"):
                enhanced_result["difficulty_level"] = ai_result["difficulty_level"]
            if ai_result.get("estimated_time"):
                enhanced_result["estimated_time"] = ai_result["estimated_time"]
                
            # Enhance materials with AI insights
            if ai_result.get("materials"):
                ai_materials = ai_result["materials"]
                template_materials = enhanced_template["materials"]
                
                # Merge materials, prioritizing AI data but adding template details
                enhanced_materials = []
                for ai_mat in ai_materials[:3]:  # Limit to first 3 AI materials
                    enhanced_mat = ai_mat.copy()
                    # Add missing fields from template
                    if not enhanced_mat.get("purpose") and template_materials:
                        enhanced_mat["purpose"] = f"Essential component for {enhanced_result['project_name']}"
                    enhanced_materials.append(enhanced_mat)
                
                # Add remaining template materials
                for template_mat in template_materials[len(ai_materials):]:
                    enhanced_materials.append(template_mat)
                    
                enhanced_result["materials"] = enhanced_materials[:7]  # Limit total materials
            
            # Enhance tools with AI insights  
            if ai_result.get("tools"):
                ai_tools = ai_result["tools"]
                template_tools = enhanced_template["tools"]
                
                enhanced_tools = []
                for ai_tool in ai_tools[:3]:  # Limit to first 3 AI tools
                    enhanced_tool = ai_tool.copy()
                    # Add missing fields from template
                    if not enhanced_tool.get("purpose") and template_tools:
                        enhanced_tool["purpose"] = f"Required for {enhanced_result['project_name']}"
                    if not enhanced_tool.get("alternatives"):
                        # Find matching template tool for alternatives
                        for template_tool in template_tools:
                            if template_tool["name"].lower() in enhanced_tool["name"].lower():
                                enhanced_tool["alternatives"] = template_tool.get("alternatives", [])
                                break
                    enhanced_tools.append(enhanced_tool)
                
                # Add remaining template tools
                for template_tool in template_tools[len(ai_tools):]:
                    enhanced_tools.append(template_tool)
                    
                enhanced_result["tools"] = enhanced_tools[:9]  # Limit total tools
            
            # Always use enhanced template data for these fields
            enhanced_result["safety_notes"] = enhanced_template["safety_notes"]
            enhanced_result["steps"] = enhanced_template["steps"]
            enhanced_result["tips_and_tricks"] = enhanced_template.get("tips_and_tricks", [])
            enhanced_result["skill_requirements"] = enhanced_template.get("skill_requirements", [])
            enhanced_result["budget_estimate"] = enhanced_template.get("budget_estimate", "")
            
            logger.info(f"Enhanced AI result with {len(enhanced_result.get('steps', []))} detailed steps")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Failed to enhance AI result: {e}")
            return ai_result  # Return original AI result if enhancement fails
    
    def _get_enhanced_template(self, project_type: str, description: str) -> Dict[str, Any]:
        """Get enhanced template based on project type"""
        templates = {
            "woodworking": {
                "project_name": "Custom Wooden Storage Cabinet",
                "description": f"A practical wooden storage cabinet project perfect for organizing tools, books, or household items. This intermediate-level woodworking project combines functionality with craftsmanship, teaching essential joinery techniques while creating a beautiful piece of furniture. {description}",
                "materials": [
                    {"name": "Pine Wood Boards", "specification": "1x12 inch, 8 feet long", "quantity": "4 boards", "estimated_price_range": "$60-80", "purpose": "Main cabinet structure and shelving"},
                    {"name": "Wood Screws", "specification": "2.5 inch drywall screws, zinc-plated", "quantity": "50 pieces", "estimated_price_range": "$8-12", "purpose": "Primary assembly fasteners"},
                    {"name": "Wood Glue", "specification": "Titebond III waterproof adhesive", "quantity": "1 bottle (16 oz)", "estimated_price_range": "$4-8", "purpose": "Strong joint bonding"},
                    {"name": "Cabinet Hinges", "specification": "European soft-close, 2 inch", "quantity": "4 pieces", "estimated_price_range": "$12-20", "purpose": "Door mounting hardware"},
                    {"name": "Wood Stain", "specification": "Minwax Dark Walnut, oil-based", "quantity": "1 quart", "estimated_price_range": "$8-15", "purpose": "Protective finish and aesthetics"},
                    {"name": "Sandpaper Assortment", "specification": "120, 220, 320 grit sheets", "quantity": "1 pack each", "estimated_price_range": "$10-18", "purpose": "Surface preparation and smoothing"}
                ],
                "tools": [
                    {"name": "Circular Saw", "necessity": "Essential", "purpose": "Primary cutting tool for lumber", "alternatives": ["Miter saw", "Table saw"]},
                    {"name": "Power Drill", "necessity": "Essential", "purpose": "Drilling pilot holes and driving screws", "alternatives": ["Impact driver", "Cordless drill"]},
                    {"name": "Measuring Tape", "necessity": "Essential", "purpose": "Accurate measurements and layout", "alternatives": ["Ruler", "Folding rule"]},
                    {"name": "Random Orbital Sander", "necessity": "Essential", "purpose": "Smooth surface preparation", "alternatives": ["Hand sanding", "Palm sander"]},
                    {"name": "Level", "necessity": "Essential", "purpose": "Ensuring straight and level assembly", "alternatives": ["Straight edge", "Laser level"]},
                    {"name": "Clamps", "necessity": "Essential", "purpose": "Holding pieces during glue-up", "alternatives": ["Bar clamps", "Pipe clamps"]},
                    {"name": "Safety Glasses", "necessity": "Essential", "purpose": "Eye protection during all operations", "alternatives": ["Safety goggles", "Face shield"]}
                ],
                "difficulty_level": "intermediate",
                "estimated_time": "6-8 hours over 2-3 days",
                "budget_estimate": "$120-180 total project cost",
                "skill_requirements": ["Basic power tool operation", "Understanding of wood grain", "Accurate measuring abilities"],
                "safety_notes": [
                    "Always wear safety glasses when cutting, drilling, or sanding",
                    "Use dust mask when sanding to prevent inhalation of particles",
                    "Ensure proper ventilation when applying stain or finish",
                    "Keep workspace clean and well-organized to prevent accidents",
                    "Check that all power tools are in good working condition before use",
                    "Never remove safety guards from power tools",
                    "Unplug tools when changing blades or bits"
                ],
                "steps": [
                    "1. Safety First: Put on safety glasses and work gloves. Ensure your workspace is well-ventilated and clean. Check all tools are in good working condition.",
                    "2. Measure and Plan: Using measuring tape, carefully measure and mark all cut lines on the wood boards. Create a detailed cutting list and double-check all measurements before cutting.",
                    "3. Cut the Wood: Use a circular saw or miter saw to cut the wood pieces according to your measurements. Cut slowly and steadily, letting the blade do the work. Sand cut edges smooth with 120-grit sandpaper.",
                    "4. Prepare Joints: If using pocket holes, drill them now with the pocket hole jig. For traditional joinery, mark and cut dadoes or rabbets as needed.",
                    "5. Pre-drill Pilot Holes: Use the power drill with a bit slightly smaller than your screws to pre-drill pilot holes. This prevents wood splitting and ensures clean assembly.",
                    "6. Test Fit Assembly: Dry-fit all pieces together without glue to ensure everything fits properly. Make any necessary adjustments now.",
                    "7. Apply Wood Glue: Apply a thin, even layer of wood glue to joining surfaces. Work quickly but carefully as wood glue begins to set within 10-15 minutes.",
                    "8. Assemble Frame: Clamp pieces together and secure with wood screws. Use a level to ensure everything is square and plumb. Wipe away excess glue immediately.",
                    "9. Install Shelves: Once the main frame is assembled and dry, install interior shelves using the same glue and screw technique.",
                    "10. Initial Sanding: Sand all surfaces starting with 120-grit, then progress to 220-grit sandpaper for a smooth finish. Always sand with the grain, never against it.",
                    "11. Clean Surface: Remove all dust with a tack cloth or compressed air. Any dust left on the surface will show through the stain.",
                    "12. Apply Pre-Stain Conditioner: For even stain absorption, apply wood conditioner according to manufacturer's directions.",
                    "13. Apply Stain: Use a brush or cloth to apply wood stain evenly, working with the grain. Maintain a wet edge and wipe off excess after the recommended time.",
                    "14. Install Hardware: Once stain is completely dry, install hinges, door handles, and any other hardware. Use a drill and appropriate bits for clean holes.",
                    "15. Final Assembly: Mount doors, adjust hinges for proper alignment, and test all moving parts. Make any final adjustments needed.",
                    "16. Quality Check: Inspect all joints, sand any rough spots, ensure all hardware is tight, and verify the cabinet is sturdy and safe to use.",
                    "17. Final Finish: Apply a protective topcoat if desired (polyurethane or paste wax) for added durability and beauty."
                ],
                "tips_and_tricks": [
                    "Always measure twice, cut once - mistakes in cutting are difficult to fix",
                    "Use a stop block when making multiple cuts of the same length",
                    "Apply stain with a brush and wipe with a rag for even coverage",
                    "Let each coat of finish cure completely before applying the next",
                    "Keep a damp rag nearby when gluing to clean up excess immediately"
                ]
            }
        }
        
        return templates.get(project_type, templates["woodworking"])

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
            "category": "power_tools",
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
            "confidence": 0.92,
            "specifications": {
                "voltage": "20V MAX",
                "chuck_size": "1/2 inch keyless",
                "speed": "0-450/0-1500 RPM"
            },
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