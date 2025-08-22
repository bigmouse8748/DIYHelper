"""
Smart Tool Finder Agent - Interactive Tool Search and Recommendation
Intelligent conversational agent for finding specific tools based on user requirements using OpenAI API
"""
import asyncio
import logging
import json
import re
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseAgent, AgentResult
import openai

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class SmartToolFinderAgent(BaseAgent):
    """Intelligent conversational agent for finding tools based on user requirements"""
    
    def __init__(self):
        super().__init__(
            name="smart_tool_finder",
            config={
                "description": "Interactive tool search with conversation and filtering",
                "max_concurrent_tasks": 2,
                "timeout_seconds": 30,
                "features": ["conversation", "web_search", "filtering", "reasoning"]
            }
        )
        
        # Tool knowledge base for intelligent matching
        self.tool_knowledge = {
            "wood_joining": {
                "keywords": ["joint", "join", "connect", "attach", "wood", "lumber", "board"],
                "tools": [
                    {
                        "name": "Biscuit Joiner",
                        "description": "Creates strong invisible joints in wood",
                        "difficulty": "intermediate",
                        "power_type": "electric",
                        "price_range": "$100-200",
                        "use_cases": ["cabinet making", "furniture", "edge joining"],
                        "brands": ["DeWalt", "Porter-Cable", "Makita"],
                        "reason": "Perfect for creating strong, invisible joints in wood panels and boards"
                    },
                    {
                        "name": "Pocket Hole Jig",
                        "description": "Creates angled holes for hidden screws",
                        "difficulty": "beginner",
                        "power_type": "manual",
                        "price_range": "$20-80",
                        "use_cases": ["face frames", "shelving", "quick joints"],
                        "brands": ["Kreg", "Milescraft", "General Tools"],
                        "reason": "Easy to use for beginners, creates strong and quick wood joints"
                    },
                    {
                        "name": "Domino Joiner",
                        "description": "Professional loose tenon joinery system",
                        "difficulty": "professional",
                        "power_type": "electric",
                        "price_range": "$800-1200",
                        "use_cases": ["furniture making", "cabinetry", "precision joints"],
                        "brands": ["Festool"],
                        "reason": "Professional-grade tool for precise, strong mortise and tenon joints"
                    },
                    {
                        "name": "Wood Glue and Clamps",
                        "description": "Traditional wood joining method",
                        "difficulty": "beginner",
                        "power_type": "manual",
                        "price_range": "$30-100",
                        "use_cases": ["edge gluing", "laminating", "basic repairs"],
                        "brands": ["Titebond", "Gorilla Glue", "Bessey"],
                        "reason": "Most fundamental and reliable method for joining wood pieces"
                    },
                    {
                        "name": "Dowel Jig",
                        "description": "Creates precise holes for dowel joints",
                        "difficulty": "intermediate",
                        "power_type": "manual",
                        "price_range": "$40-120",
                        "use_cases": ["furniture assembly", "cabinet doors", "alignment"],
                        "brands": ["Dowl-It", "General Tools", "Wolfcraft"],
                        "reason": "Creates precise, strong joints using wooden dowels"
                    }
                ]
            },
            "cutting": {
                "keywords": ["cut", "saw", "slice", "trim", "split"],
                "tools": [
                    {
                        "name": "Circular Saw",
                        "description": "Versatile power saw for straight cuts",
                        "difficulty": "intermediate",
                        "power_type": "electric",
                        "price_range": "$60-200",
                        "use_cases": ["crosscuts", "rip cuts", "sheet goods"],
                        "brands": ["DeWalt", "Makita", "Milwaukee"],
                        "reason": "Most versatile saw for general cutting tasks"
                    },
                    {
                        "name": "Miter Saw",
                        "description": "Precision saw for accurate crosscuts and miters",
                        "difficulty": "beginner",
                        "power_type": "electric",
                        "price_range": "$150-500",
                        "use_cases": ["trim work", "framing", "precise angles"],
                        "brands": ["DeWalt", "Bosch", "Hitachi"],
                        "reason": "Best for precise, repeatable crosscuts and miter cuts"
                    }
                ]
            },
            "drilling": {
                "keywords": ["drill", "hole", "bore", "pierce"],
                "tools": [
                    {
                        "name": "Cordless Drill",
                        "description": "Portable drilling and driving tool",
                        "difficulty": "beginner",
                        "power_type": "electric",
                        "price_range": "$50-150",
                        "use_cases": ["holes", "driving screws", "general purpose"],
                        "brands": ["DeWalt", "Milwaukee", "Ryobi"],
                        "reason": "Essential tool for drilling holes and driving fasteners"
                    }
                ]
            },
            "sanding": {
                "keywords": ["sand", "smooth", "finish", "polish"],
                "tools": [
                    {
                        "name": "Random Orbital Sander",
                        "description": "Smooth finish sander with minimal marks",
                        "difficulty": "beginner",
                        "power_type": "electric",
                        "price_range": "$80-200",
                        "use_cases": ["finish sanding", "paint prep", "smooth surfaces"],
                        "brands": ["Bosch", "DeWalt", "Makita"],
                        "reason": "Best for achieving smooth, swirl-free finishes"
                    }
                ]
            }
        }
        
        # Retailer search URLs
        self.retailer_urls = {
            "amazon": "https://www.amazon.com/s?k=",
            "home_depot": "https://www.homedepot.com/s/",
            "lowes": "https://www.lowes.com/search?searchTerm=",
            "walmart": "https://www.walmart.com/search/?query=",
            "harbor_freight": "https://www.harborfreight.com/catalogsearch/result/?q="
        }

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute smart tool finder task"""
        return await self.process_conversation(input_data)

    async def process_conversation(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process conversational tool finding request using OpenAI API"""
        try:
            user_query = input_data.get("query", "").strip()
            filters = input_data.get("filters", {})
            conversation_history = input_data.get("conversation_history", [])
            user_context = input_data.get("user_context", {})
            
            logger.info(f"Processing tool finder query: {user_query}")
            
            if not user_query:
                return self._create_welcome_response()
            
            # Call OpenAI API to analyze user request and generate tool recommendations
            ai_response = await self._call_openai_for_tool_recommendations(
                user_query, filters, conversation_history, user_context
            )
            
            # Parse and enhance AI response
            enhanced_response = await self._enhance_ai_response(ai_response, filters)
            
            return AgentResult(
                success=True,
                data=enhanced_response,
                agent_name=self.name,
                execution_time=2.5
            )
            
        except Exception as e:
            logger.error(f"Smart tool finder failed: {str(e)}")
            # Fallback to predefined response if OpenAI fails
            fallback_response = await self._create_fallback_response(input_data.get("query", ""))
            return AgentResult(
                success=True,
                data=fallback_response,
                agent_name=self.name,
                execution_time=0.5
            )

    def _create_welcome_response(self) -> AgentResult:
        """Create welcome response for new conversations"""
        response = {
            "message": "Hi! I'm your Smart Tool Finder assistant. Tell me what you want to accomplish, and I'll help you find the perfect tools for the job.",
            "suggestions": [
                "I want to join two pieces of wood",
                "I need to cut lumber for a project",
                "I want to drill precise holes",
                "I need to sand a wooden surface smooth"
            ],
            "tools": [],
            "conversation_type": "welcome"
        }
        
        return AgentResult(
            success=True,
            data=response,
            agent_name=self.name,
            execution_time=0.1
        )

    async def _analyze_user_intent(self, query: str, history: List[Dict]) -> Dict[str, Any]:
        """Analyze user intent from their query"""
        intent = {
            "task_type": None,
            "materials": [],
            "requirements": [],
            "context": query
        }
        
        # Convert query to lowercase for better matching
        query_lower = query.lower()
        
        # Extract task type based on keywords with more precise matching
        for task_type, task_info in self.tool_knowledge.items():
            for keyword in task_info["keywords"]:
                if keyword in query_lower:
                    intent["task_type"] = task_type
                    break
            if intent["task_type"]:  # Break outer loop if found
                break
        
        # Extract materials mentioned
        materials = ["wood", "metal", "plastic", "concrete", "drywall", "tile"]
        intent["materials"] = [mat for mat in materials if mat in query_lower]
        
        # Extract specific requirements
        if any(word in query_lower for word in ["precise", "accurate", "precision"]):
            intent["requirements"].append("precision")
        if any(word in query_lower for word in ["quick", "fast", "speed"]):
            intent["requirements"].append("speed")
        if any(word in query_lower for word in ["strong", "durable", "strength"]):
            intent["requirements"].append("strength")
        if any(word in query_lower for word in ["beginner", "easy", "simple"]):
            intent["requirements"].append("beginner_friendly")
        
        return intent

    async def _find_matching_tools(self, intent: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict]:
        """Find tools that match the user's intent and filters"""
        matches = []
        
        task_type = intent.get("task_type")
        if not task_type or task_type not in self.tool_knowledge:
            # If no specific task type found, search across all categories
            all_tools = []
            for category in self.tool_knowledge.values():
                all_tools.extend(category["tools"])
            return self._apply_filters(all_tools[:5], filters)
        
        # Get tools for the specific task type
        tools = self.tool_knowledge[task_type]["tools"]
        
        # Score tools based on requirements
        scored_tools = []
        for tool in tools:
            score = self._calculate_tool_score(tool, intent, filters)
            if score > 0:
                tool_copy = tool.copy()
                tool_copy["match_score"] = score
                scored_tools.append(tool_copy)
        
        # Sort by score and apply filters
        scored_tools.sort(key=lambda x: x["match_score"], reverse=True)
        filtered_tools = self._apply_filters(scored_tools, filters)
        
        # Enhance with shopping links
        enhanced_tools = []
        for tool in filtered_tools[:5]:  # Top 5 tools
            enhanced_tool = await self._enhance_tool_with_shopping_links(tool)
            enhanced_tools.append(enhanced_tool)
        
        return enhanced_tools

    def _calculate_tool_score(self, tool: Dict, intent: Dict, filters: Dict) -> float:
        """Calculate how well a tool matches the user's intent"""
        score = 1.0  # Base score
        
        requirements = intent.get("requirements", [])
        
        # Boost score for requirement matches
        if "precision" in requirements and "precision" in tool.get("use_cases", []):
            score += 0.5
        if "beginner_friendly" in requirements and tool.get("difficulty") == "beginner":
            score += 0.3
        if "speed" in requirements and "quick" in tool.get("description", "").lower():
            score += 0.2
        
        return score

    def _apply_filters(self, tools: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply user-selected filters to tool list"""
        if not filters:
            return tools
        
        filtered = tools.copy()
        
        # Price filter
        price_range = filters.get("price_range")
        if price_range:
            filtered = [t for t in filtered if self._matches_price_range(t, price_range)]
        
        # Difficulty filter
        difficulty = filters.get("difficulty")
        if difficulty:
            filtered = [t for t in filtered if t.get("difficulty") == difficulty]
        
        # Power type filter
        power_type = filters.get("power_type")
        if power_type:
            filtered = [t for t in filtered if t.get("power_type") == power_type]
        
        return filtered

    def _matches_price_range(self, tool: Dict, price_range: str) -> bool:
        """Check if tool matches the specified price range"""
        tool_price = tool.get("price_range", "$0-50")
        
        # Extract price numbers from tool price range
        tool_prices = re.findall(r'\d+', tool_price)
        if not tool_prices:
            return True
        
        tool_max = int(tool_prices[-1])
        
        if price_range == "under_50":
            return tool_max <= 50
        elif price_range == "50_150":
            return 50 <= tool_max <= 150
        elif price_range == "150_500":
            return 150 <= tool_max <= 500
        elif price_range == "over_500":
            return tool_max > 500
        
        return True

    async def _enhance_tool_with_shopping_links(self, tool: Dict) -> Dict:
        """Add shopping links and enhanced information to tool"""
        enhanced = tool.copy()
        
        # Create search query
        tool_name = tool.get("name", "")
        brands = tool.get("brands", [])
        search_query = f"{tool_name} {brands[0] if brands else ''}"
        search_query = search_query.replace(" ", "+")
        
        # Add shopping links
        shopping_links = []
        for retailer, base_url in self.retailer_urls.items():
            shopping_links.append({
                "retailer": retailer.replace("_", " ").title(),
                "url": f"{base_url}{search_query}",
                "search_query": search_query.replace("+", " ")
            })
        
        enhanced.update({
            "shopping_links": shopping_links,
            "estimated_price": tool.get("price_range", "Varies"),
            "image_url": f"https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=300&h=200&fit=crop&q=80",
            "timestamp": datetime.now().isoformat()
        })
        
        return enhanced

    async def _generate_response(self, query: str, intent: Dict, tools: List[Dict], filters: Dict) -> Dict:
        """Generate conversational response with tool recommendations"""
        
        if not tools:
            return {
                "message": "I couldn't find any tools that match your specific requirements. Could you provide more details about what you're trying to accomplish?",
                "suggestions": [
                    "Try describing your project in more detail",
                    "Mention specific materials you're working with",
                    "Let me know your experience level"
                ],
                "tools": [],
                "conversation_type": "clarification"
            }
        
        # Generate contextual message
        task_type = intent.get("task_type", "")
        message_parts = []
        
        if task_type:
            # Create human-readable task descriptions
            task_descriptions = {
                "wood_joining": "wood joining",
                "cutting": "cutting",
                "drilling": "drilling", 
                "sanding": "sanding"
            }
            readable_task = task_descriptions.get(task_type, task_type.replace("_", " "))
            message_parts.append(f"For {readable_task}, I found {len(tools)} great tool options:")
        else:
            message_parts.append(f"Based on your query, here are {len(tools)} recommended tools:")
        
        # Add filter context
        if filters:
            filter_desc = []
            if filters.get("price_range"):
                filter_desc.append(f"in your price range")
            if filters.get("difficulty"):
                filter_desc.append(f"suitable for {filters['difficulty']} level")
            if filter_desc:
                message_parts.append(f" (filtered {', '.join(filter_desc)})")
        
        message = "".join(message_parts)
        
        # Generate follow-up suggestions
        suggestions = [
            "Tell me more about your specific project",
            "I need something cheaper/more expensive",
            "Show me electric/manual tools only",
            "What about beginner-friendly options?"
        ]
        
        return {
            "message": message,
            "suggestions": suggestions,
            "tools": tools,
            "conversation_type": "recommendation",
            "intent_summary": intent
        }

    async def _call_openai_for_tool_recommendations(self, user_query: str, filters: Dict, 
                                                   conversation_history: List[Dict], 
                                                   user_context: Dict) -> Dict:
        """Call OpenAI API to get intelligent tool recommendations"""
        try:
            # Build context from conversation history
            context_messages = []
            for entry in conversation_history[-3:]:  # Last 3 exchanges
                if 'user' in entry:
                    context_messages.append(f"User: {entry['user']}")
                if 'assistant' in entry:
                    context_messages.append(f"Assistant: {entry['assistant']}")
            
            conversation_context = "\n".join(context_messages) if context_messages else "This is a new conversation."
            
            # Build filter context
            filter_context = ""
            if filters:
                filter_parts = []
                if filters.get("price_range"):
                    price_map = {
                        "under_50": "under $50",
                        "50_150": "$50-150", 
                        "150_500": "$150-500",
                        "over_500": "over $500"
                    }
                    filter_parts.append(f"Price range: {price_map.get(filters['price_range'], filters['price_range'])}")
                if filters.get("difficulty"):
                    filter_parts.append(f"Difficulty level: {filters['difficulty']}")
                if filters.get("power_type"):
                    filter_parts.append(f"Power type: {filters['power_type']}")
                
                if filter_parts:
                    filter_context = f"\nUser preferences: {', '.join(filter_parts)}"

            # Create comprehensive prompt for OpenAI
            system_prompt = """You are an expert DIY tool consultant with advanced intent recognition capabilities. Your job is to intelligently analyze user requests and provide appropriate responses based on their intent.

## INTENT ANALYSIS RULES:

**PRODUCT RECOMMENDATION INTENT** - User wants specific tools/products (respond with detailed recommendations):
- Keywords indicating purchase intent: "buy", "purchase", "recommend", "suggest", "need tools for", "what tools", "which tools", "best tools"
- Specific project mentions: "I want to cut wood", "need to drill holes", "painting walls"
- Comparison requests: "alternatives", "options", "different brands", "choices"
- Budget-related: "affordable", "cheap", "expensive", "budget", "price range"

**INFORMATION GATHERING INTENT** - User question is vague/general (respond with clarifying questions):
- General inquiries: "how to do DIY", "getting started", "what do I need"
- Vague projects: "home improvement", "fixing things", "building something"
- Ambiguous requests: "help me", "advice", "suggestions" (without specific context)

## RESPONSE FORMATS:

### For PRODUCT RECOMMENDATION INTENT:
{
    "intent_type": "product_recommendation",
    "task_analysis": "Detailed analysis of the specific task user wants to accomplish",
    "recommended_tools": [
        // MINIMUM 3 tools, MAXIMUM 5 tools
        {
            "name": "Tool Name",
            "description": "What this tool does and key features",
            "difficulty": "beginner/intermediate/professional", 
            "power_type": "electric/manual/pneumatic/cordless",
            "price_range": "$X-Y",
            "brands": ["Brand1", "Brand2", "Brand3"], // At least 2 different brands
            "reason": "Specific reason why this tool is perfect for the user's needs",
            "use_cases": ["specific use case 1", "specific use case 2"],
            "pros": ["advantage 1", "advantage 2"],
            "cons": ["limitation 1", "limitation 2"]
        }
    ],
    "message": "Professional explanation of recommendations with comparison guidance",
    "suggestions": ["Product-related follow-up 1", "Usage question 2", "Budget alternative 3"]
}

### For INFORMATION GATHERING INTENT:
{
    "intent_type": "information_gathering", 
    "task_analysis": "Analysis of what information is needed to help the user",
    "recommended_tools": [], // Empty array
    "message": "Helpful response acknowledging their request and explaining why more information is needed",
    "suggestions": ["Specific clarifying question 1", "Project scope question 2", "Budget/experience question 3", "Timeline question 4"]
}

## CRITICAL REQUIREMENTS:
1. **Product Recommendations**: MUST include minimum 3 tools with diverse price points and difficulty levels
2. **Brand Diversity**: Each tool should include multiple brand options (DeWalt, Milwaukee, Makita, Bosch, Ryobi, Black+Decker, etc.)
3. **Practical Focus**: Only recommend tools actually available for purchase from major retailers
4. **Smart Follow-up**: Suggestions should be contextually relevant and helpful for next steps
5. **Budget Consciousness**: Always include budget-friendly and premium options when recommending products

Analyze the user's intent carefully and respond appropriately. Be conversational but professional."""

            user_prompt = f"""User request: "{user_query}"

Previous conversation context:
{conversation_context}

{filter_context}

Please analyze this request and recommend the most appropriate tools. Be specific about brands, models when possible, and explain why each tool is recommended for this particular task."""

            # Call OpenAI API
            client = openai.OpenAI(api_key=openai.api_key)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
            )
            
            # Parse response
            ai_content = response.choices[0].message.content
            logger.info(f"OpenAI response received: {len(ai_content)} characters")
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(ai_content)
                return parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._parse_text_response(ai_content, user_query)
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise e

    def _parse_text_response(self, ai_content: str, user_query: str) -> Dict:
        """Parse non-JSON AI response into structured format"""
        return {
            "intent_type": "product_recommendation",  # Default to product recommendation for fallback
            "task_analysis": f"Analysis of user request: {user_query}",
            "recommended_tools": [
                {
                    "name": "AI-Recommended Tool",
                    "description": "Tool recommendation based on AI analysis",
                    "difficulty": "intermediate",
                    "power_type": "electric",
                    "price_range": "$50-200",
                    "brands": ["Various"],
                    "reason": ai_content[:200] + "..." if len(ai_content) > 200 else ai_content,
                    "use_cases": ["general purpose"]
                }
            ],
            "message": f"Based on your request '{user_query}', here are my recommendations:",
            "suggestions": [
                "Can you provide more details about your project?",
                "What's your experience level with tools?",
                "Do you have a specific budget in mind?"
            ]
        }

    async def _enhance_ai_response(self, ai_response: Dict, filters: Dict) -> Dict:
        """Enhance AI response with shopping links and additional features based on intent type"""
        intent_type = ai_response.get("intent_type", "product_recommendation")
        enhanced_tools = []
        
        # Handle different intent types
        if intent_type == "information_gathering":
            # For information gathering, no tools/shopping links needed
            return {
                "message": ai_response.get("message", "I'd be happy to help! Could you provide more specific details about what you're looking for?"),
                "suggestions": ai_response.get("suggestions", [
                    "Tell me about your specific project",
                    "What's your experience level with DIY?", 
                    "Do you have a budget in mind?",
                    "What materials are you working with?"
                ]),
                "tools": [],  # No tools for information gathering
                "conversation_type": "clarification",
                "task_analysis": ai_response.get("task_analysis", ""),
                "ai_powered": True,
                "intent_type": intent_type
            }
        
        # For product recommendation intent, enhance tools with shopping links
        recommended_tools = ai_response.get("recommended_tools", [])
        
        # Ensure minimum 3 tools for product recommendations
        if intent_type == "product_recommendation" and len(recommended_tools) < 3:
            logger.warning(f"AI returned only {len(recommended_tools)} tools, but minimum 3 required for product recommendations")
        
        for tool in recommended_tools:
            enhanced_tool = tool.copy()
            
            # Generate shopping links only for product recommendations
            tool_name = tool.get("name", "")
            brands = tool.get("brands", [""])
            search_query = f"{tool_name} {brands[0] if brands else ''}".strip()
            search_query_encoded = search_query.replace(" ", "+")
            
            enhanced_tool["shopping_links"] = [
                {
                    "retailer": "Amazon",
                    "url": f"{self.retailer_urls['amazon']}{search_query_encoded}",
                    "search_query": search_query
                },
                {
                    "retailer": "Home Depot", 
                    "url": f"{self.retailer_urls['home_depot']}{search_query_encoded}",
                    "search_query": search_query
                },
                {
                    "retailer": "Lowes",
                    "url": f"{self.retailer_urls['lowes']}{search_query_encoded}",
                    "search_query": search_query
                },
                {
                    "retailer": "Walmart",
                    "url": f"{self.retailer_urls['walmart']}{search_query_encoded}",
                    "search_query": search_query
                },
                {
                    "retailer": "Harbor Freight",
                    "url": f"{self.retailer_urls['harbor_freight']}{search_query_encoded}",
                    "search_query": search_query
                }
            ]
            
            # Add additional metadata
            enhanced_tool.update({
                "estimated_price": tool.get("price_range", "Varies"),
                "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=300&h=200&fit=crop&q=80",
                "timestamp": datetime.now().isoformat(),
                "ai_recommended": True
            })
            
            enhanced_tools.append(enhanced_tool)
        
        return {
            "message": ai_response.get("message", "Here are my AI-powered tool recommendations:"),
            "suggestions": ai_response.get("suggestions", [
                "Tell me more about your project",
                "I need different options", 
                "What about budget alternatives?"
            ]),
            "tools": enhanced_tools,
            "conversation_type": "recommendation",
            "task_analysis": ai_response.get("task_analysis", ""),
            "ai_powered": True,
            "intent_type": intent_type,
            "tool_count": len(enhanced_tools)
        }

    async def _create_fallback_response(self, user_query: str) -> Dict:
        """Create fallback response when OpenAI API is unavailable"""
        return {
            "message": "I'm having trouble connecting to my AI analysis service right now, but I can still help you! Could you provide more specific details about what you're trying to accomplish?",
            "suggestions": [
                "Tell me what materials you're working with",
                "Describe your project in more detail",
                "Let me know your experience level",
                "What's your budget range?"
            ],
            "tools": [],
            "conversation_type": "clarification",
            "fallback_mode": True
        }