"""
Tool Identification Agent for recognizing tools and finding shopping links
Based on the original version from diy-agent-system
"""
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

from .base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

@dataclass
class ToolInfo:
    """Tool information structure"""
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    category: str = "unknown"
    confidence: float = 0.0
    specifications: Dict = None

@dataclass 
class ProductListing:
    """Product listing from retailer"""
    retailer: str
    title: str
    price: float
    url: str
    image_url: str
    in_stock: bool = True
    is_exact_match: bool = False

class ToolIdentificationAgentOriginal(BaseAgent):
    """Agent for identifying tools from images and finding purchase options"""
    
    def __init__(self):
        super().__init__(
            name="tool_identification_original",
            config={"description": "Original tool identification agent with advanced features"}
        )
        self.retailers = ["amazon", "home_depot", "lowes", "walmart"]
        
        # Common tool brands for pattern matching
        self.known_brands = [
            "DeWalt", "Milwaukee", "Makita", "Bosch", "Ryobi",
            "BLACK+DECKER", "Craftsman", "Stanley", "Klein Tools",
            "Ridgid", "Festool", "Hilti", "Metabo", "Porter-Cable",
            "Kobalt", "Husky", "Irwin", "Channellock", "Knipex"
        ]
        
        # Enhanced tool categories with more specific tools
        self.tool_categories = {
            "power_tools": [
                "table saw", "circular saw", "miter saw", "band saw", "jigsaw", "reciprocating saw",
                "drill", "impact driver", "hammer drill", "rotary hammer",
                "angle grinder", "bench grinder", "die grinder",
                "belt sander", "orbital sander", "palm sander", "disc sander",
                "router", "planer", "jointer", "lathe",
                "nail gun", "brad nailer", "staple gun"
            ],
            "hand_tools": [
                "hammer", "claw hammer", "ball peen hammer", "sledgehammer",
                "screwdriver", "phillips screwdriver", "flathead screwdriver",
                "wrench", "adjustable wrench", "socket wrench", "box wrench",
                "pliers", "needle nose pliers", "wire cutters", "locking pliers",
                "chisel", "hand plane", "hand saw", "hacksaw", "coping saw"
            ],
            "measuring": ["tape measure", "level", "ruler", "caliper", "square", "protractor", "micrometer"],
            "cutting": ["utility knife", "box cutter", "scissors", "snips", "shears", "wire strippers"],
            "fastening": ["clamp", "vise", "stapler", "rivet gun", "glue gun"],
            "outdoor": ["chainsaw", "string trimmer", "leaf blower", "lawn mower", "edger", "hedge trimmer"]
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute tool identification task"""
        try:
            image_data = input_data.get("image_data")
            include_alternatives = input_data.get("include_alternatives", True)
            user_membership = input_data.get("membership_level", "free")
            
            # Step 1: Identify the tool
            tool_info = await self._identify_tool(image_data)
            
            # Step 2: Search for exact matches if model is identified
            exact_matches = []
            if tool_info.model:
                exact_matches = await self._search_exact_product(
                    tool_info.brand, 
                    tool_info.model
                )
            
            # Step 3: Find alternatives or similar products
            alternatives = []
            if include_alternatives:
                max_alternatives = self._get_alternatives_limit(user_membership)
                alternatives = await self._find_alternatives(
                    tool_info,
                    max_alternatives
                )
            
            # Step 4: Get real-time prices if premium user
            if user_membership in ["premium", "pro"]:
                exact_matches = await self._update_realtime_prices(exact_matches)
                alternatives = await self._update_realtime_prices(alternatives)
            
            # Step 5: Format response
            result_data = {
                "tool_info": {
                    "name": tool_info.name,
                    "brand": tool_info.brand,
                    "model": tool_info.model,
                    "category": tool_info.category,
                    "confidence": tool_info.confidence,
                    "specifications": tool_info.specifications
                },
                "exact_matches": [self._format_product(p) for p in exact_matches],
                "alternatives": [self._format_product(p) for p in alternatives],
                "search_timestamp": datetime.utcnow().isoformat()
            }
            
            return AgentResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Tool identification failed: {str(e)}")
            return AgentResult(
                success=False,
                error=str(e)
            )
    
    async def _identify_tool(self, image_data: str) -> ToolInfo:
        """Identify tool from image using vision API or advanced pattern matching"""
        try:
            # Try OpenAI Vision API first
            result = await self._identify_with_openai_vision(image_data)
            if result:
                return result
        except Exception as e:
            logger.warning(f"OpenAI Vision API failed: {str(e)}, falling back to intelligent analysis")
        
        # Fallback to intelligent pattern-based identification
        return await self._identify_with_intelligent_analysis(image_data)
    
    async def _identify_with_openai_vision(self, image_data: str) -> Optional[ToolInfo]:
        """Identify tool using OpenAI Vision API"""
        import os
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not found")
            return None
        
        try:
            import openai
            
            # Convert base64 to proper format
            image_url = f"data:image/jpeg;base64,{image_data}"
            
            # Create OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # Call Vision API with improved model
            response = client.chat.completions.create(
                model="gpt-4o",  # Updated to latest model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are a professional tool identification expert. Carefully analyze this image and identify the specific tool shown.

CRITICAL DISTINCTIONS - Pay close attention to these key differences:

SAW TYPES:
- TABLE SAW: Large stationary tool with flat table surface, blade extends UP through table slot, fence rail system, heavy base/stand
- CIRCULAR SAW: Handheld tool with circular blade guard, top handle, compact size, blade guard retracts
- MITER SAW: Stationary saw with pivoting arm that cuts DOWN onto material, has miter fence/gauge, blade enclosed in guard
- BAND SAW: Vertical frame with continuous loop blade running on upper/lower wheels, table for material support
- JIGSAW: Small handheld saw with thin straight reciprocating blade extending from bottom

DRILL TYPES:
- DRILL: Keyless chuck (three-jaw), usually has clutch settings, for drilling holes
- IMPACT DRIVER: Hex bit chuck (1/4"), compact body, for driving screws/bolts
- HAMMER DRILL: Similar to drill but bulkier, has hammer/drill mode selector

SANDER TYPES:
- BELT SANDER: Uses continuous sanding belt, rectangular shape
- ORBITAL SANDER: Round or square pad, vibrates in small orbits
- PALM SANDER: Small rectangular pad, fits in palm of hand

GRINDER TYPES:
- ANGLE GRINDER: Side handle, disc guard, larger diameter disc (4-7")
- DIE GRINDER: Pencil-shaped, small collet chuck, precise work

Analyze these visual cues:
1. OVERALL SIZE & SHAPE (handheld vs stationary)
2. TABLE SURFACE (present on table saw, miter saw, band saw)
3. HANDLE POSITION (top, side, grip style)
4. BLADE/BIT TYPE (circular, straight, loop, chuck type)
5. GUARD CONFIGURATION
6. BRAND LOGOS and MODEL NUMBERS
7. Power source (cord, battery pack)

Respond ONLY with this exact JSON format:
{
    "name": "Specific tool name",
    "brand": "Brand name or null",
    "model": "Model number or null",
    "category": "power_tools, hand_tools, measuring, cutting, fastening, outdoor, or unknown",
    "confidence": 0.85,
    "specifications": {"key": "value"}
}

Be EXTREMELY precise with tool identification. If unsure between similar tools, choose the most likely based on visible features."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.1  # Lower temperature for more consistent results
            )
            
            # Parse response with improved error handling
            content = response.choices[0].message.content
            logger.info(f"OpenAI Vision response: {content}")
            
            # Extract and parse JSON from response
            import json
            import re
            
            # Try multiple JSON extraction methods
            json_data = None
            
            # Method 1: Look for complete JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error with method 1: {e}")
            
            # Method 2: Clean and try again if method 1 failed
            if not json_data:
                try:
                    # Remove markdown code blocks if present
                    cleaned_content = re.sub(r'```json\s*|\s*```', '', content)
                    cleaned_content = re.sub(r'^[^{]*', '', cleaned_content)  # Remove text before {
                    cleaned_content = re.sub(r'}[^}]*$', '}', cleaned_content)  # Remove text after }
                    json_data = json.loads(cleaned_content)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error with method 2: {e}")
            
            if json_data:
                # Validate required fields and create ToolInfo
                name = json_data.get("name", "Unknown Tool")
                if name == "Unknown Tool" or not name:
                    name = "Unidentified Tool"
                
                brand = json_data.get("brand")
                if brand == "null" or brand == "":
                    brand = None
                    
                model = json_data.get("model")
                if model == "null" or model == "":
                    model = None
                
                category = json_data.get("category", "unknown")
                if category not in ["power_tools", "hand_tools", "measuring", "cutting", "fastening", "outdoor"]:
                    category = "unknown"
                
                try:
                    confidence = float(json_data.get("confidence", 0.5))
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1 range
                except (ValueError, TypeError):
                    confidence = 0.5
                
                specs = json_data.get("specifications", {})
                if not isinstance(specs, dict):
                    specs = {}
                
                return ToolInfo(
                    name=name,
                    brand=brand,
                    model=model,
                    category=category,
                    confidence=confidence,
                    specifications=specs
                )
            else:
                logger.error(f"Failed to extract valid JSON from response: {content}")
                return None
            
        except Exception as e:
            logger.error(f"OpenAI Vision API error: {str(e)}")
            return None
        
        return None
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for tool identification"""
        return "image_data" in input_data
    
    # Additional methods would be copied from the original file...
    # This is a partial implementation to demonstrate the concept