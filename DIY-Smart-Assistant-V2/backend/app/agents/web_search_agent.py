"""
Web Search Agent for Finding Cost-Effective Products
Searches the web for high-quality, budget-friendly tools and materials
"""
import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class WebSearchAgent(BaseAgent):
    """Agent for searching the web to find cost-effective product options"""
    
    def __init__(self):
        super().__init__(
            name="web_search_agent",
            config={
                "description": "Searches web for high-quality, budget-friendly tools and materials",
                "max_results_per_item": 5,
                "search_timeout": 30,
                "features": ["price_comparison", "review_analysis", "quality_scoring"]
            }
        )
        
        # Major retailer search URLs for tools and materials
        self.search_engines = [
            {
                "name": "Home Depot",
                "base_url": "https://www.homedepot.com/s/{}",
                "priority": 1,
                "strengths": ["tools", "hardware", "building materials"]
            },
            {
                "name": "Lowes",
                "base_url": "https://www.lowes.com/search?searchTerm={}",
                "priority": 1,
                "strengths": ["tools", "appliances", "home improvement"]
            },
            {
                "name": "Amazon",
                "base_url": "https://www.amazon.com/s?k={}",
                "priority": 2,
                "strengths": ["variety", "reviews", "quick delivery"]
            },
            {
                "name": "Harbor Freight",
                "base_url": "https://www.harborfreight.com/catalogsearch/result/?q={}",
                "priority": 3,
                "strengths": ["budget tools", "value pricing", "frequent sales"]
            },
            {
                "name": "Northern Tool",
                "base_url": "https://www.northerntool.com/shop/tools/search?searchTerms={}",
                "priority": 2,
                "strengths": ["professional tools", "durability", "heavy duty"]
            }
        ]
        
        # Product quality indicators for analysis
        self.quality_indicators = {
            "excellent": ["professional", "commercial grade", "heavy duty", "lifetime warranty", "5 year warranty"],
            "very_good": ["contractor grade", "mid-range", "3 year warranty", "good quality", "reliable"],
            "good": ["homeowner grade", "standard", "1 year warranty", "basic", "entry level"],
            "budget": ["economy", "basic", "light duty", "90 day warranty", "disposable"]
        }
        
        # Price range analysis for different categories
        self.price_ranges = {
            "power_tools": {
                "budget": (20, 60),
                "mid_range": (60, 150),
                "professional": (150, 400)
            },
            "hand_tools": {
                "budget": (5, 25),
                "mid_range": (25, 75),
                "professional": (75, 200)
            },
            "materials": {
                "budget": (10, 50),
                "mid_range": (50, 150),
                "professional": (150, 500)
            }
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute web search for tools and materials"""
        try:
            items_to_search = input_data.get("items", [])
            if not items_to_search:
                return AgentResult(
                    success=False,
                    error="No items provided for web search"
                )
            
            logger.info(f"Starting web search for {len(items_to_search)} items")
            
            search_results = []
            for item in items_to_search:
                item_name = item.get("name", "")
                item_type = item.get("type", "tool")
                
                if item_name:
                    logger.info(f"Searching for: {item_name} (type: {item_type})")
                    item_results = await self._search_item(item_name, item_type)
                    
                    if item_results:
                        search_results.append({
                            "item_name": item_name,
                            "item_type": item_type,
                            "search_results": item_results,
                            "top_recommendations": self._get_top_recommendations(item_results),
                            "price_analysis": self._analyze_prices(item_results),
                            "quality_summary": self._analyze_quality(item_results)
                        })
            
            # Generate comprehensive shopping guide
            shopping_guide = self._generate_shopping_guide(search_results)
            
            result_data = {
                "search_results": search_results,
                "shopping_guide": shopping_guide,
                "total_items_searched": len(items_to_search),
                "successful_searches": len(search_results),
                "search_timestamp": datetime.utcnow().isoformat()
            }
            
            return AgentResult(
                success=True,
                data=result_data,
                execution_time=2.5,
                metadata={"search_engine_count": len(self.search_engines)}
            )
            
        except Exception as e:
            logger.error(f"Web search agent error: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                error=f"Web search failed: {str(e)}"
            )
    
    async def _search_item(self, item_name: str, item_type: str) -> List[Dict]:
        """Search for a specific item across multiple retailers"""
        search_results = []
        
        # Clean and optimize search term
        search_term = self._optimize_search_term(item_name, item_type)
        
        for engine in self.search_engines:
            try:
                # Generate search URL
                search_url = engine["base_url"].format(search_term.replace(" ", "+"))
                
                # Simulate product search (in real implementation, would use web scraping or APIs)
                mock_results = await self._simulate_search(engine, search_term, item_type)
                
                for result in mock_results:
                    result["retailer"] = engine["name"]
                    result["search_url"] = search_url
                    result["retailer_priority"] = engine["priority"]
                    search_results.append(result)
                    
            except Exception as e:
                logger.warning(f"Search failed for {engine['name']}: {str(e)}")
                continue
        
        # Sort by quality score and price value
        search_results.sort(key=lambda x: (x.get("quality_score", 0), -x.get("price", float('inf'))), reverse=True)
        
        return search_results[:5]  # Return top 5 results
    
    def _optimize_search_term(self, item_name: str, item_type: str) -> str:
        """Optimize search term for better results"""
        # Remove common words that might dilute search
        stop_words = ["the", "a", "an", "and", "or", "but", "with", "for"]
        
        words = item_name.lower().split()
        optimized_words = [word for word in words if word not in stop_words]
        
        # Add type-specific keywords for better targeting
        if item_type == "tool":
            if "drill" in item_name.lower():
                optimized_words.append("cordless")
            elif "saw" in item_name.lower():
                optimized_words.append("electric")
        elif item_type == "material":
            if "wood" in item_name.lower():
                optimized_words.append("lumber")
        
        return " ".join(optimized_words)
    
    async def _simulate_search(self, engine: Dict, search_term: str, item_type: str) -> List[Dict]:
        """Simulate web search results (in real implementation, would use actual web scraping/APIs)"""
        
        # Generate realistic product results based on retailer strengths
        results = []
        
        if engine["name"] == "Home Depot":
            results = self._generate_home_depot_results(search_term, item_type)
        elif engine["name"] == "Lowes":
            results = self._generate_lowes_results(search_term, item_type)
        elif engine["name"] == "Amazon":
            results = self._generate_amazon_results(search_term, item_type)
        elif engine["name"] == "Harbor Freight":
            results = self._generate_harbor_freight_results(search_term, item_type)
        elif engine["name"] == "Northern Tool":
            results = self._generate_northern_tool_results(search_term, item_type)
        
        return results
    
    def _generate_home_depot_results(self, search_term: str, item_type: str) -> List[Dict]:
        """Generate realistic Home Depot search results"""
        base_results = [
            {
                "title": f"RIDGID {search_term.title()} - Professional Grade",
                "price": self._generate_realistic_price(item_type, "mid_range"),
                "rating": 4.3,
                "review_count": 1247,
                "features": ["Professional grade", "3-year warranty", "Lifetime service agreement"],
                "availability": "In stock",
                "shipping": "Free store pickup"
            },
            {
                "title": f"RYOBI ONE+ {search_term.title()} - DIY Series",
                "price": self._generate_realistic_price(item_type, "budget"),
                "rating": 4.1,
                "review_count": 856,
                "features": ["18V ONE+ compatible", "Compact design", "3-year warranty"],
                "availability": "In stock",
                "shipping": "Free store pickup"
            }
        ]
        
        # Add quality scores
        for result in base_results:
            result["quality_score"] = self._calculate_quality_score(result)
            result["value_score"] = self._calculate_value_score(result)
        
        return base_results
    
    def _generate_lowes_results(self, search_term: str, item_type: str) -> List[Dict]:
        """Generate realistic Lowes search results"""
        base_results = [
            {
                "title": f"Kobalt {search_term.title()} - Contractor Series",
                "price": self._generate_realistic_price(item_type, "mid_range"),
                "rating": 4.4,
                "review_count": 923,
                "features": ["Contractor grade", "5-year warranty", "Brushless motor"],
                "availability": "In stock",
                "shipping": "Free shipping to store"
            },
            {
                "title": f"CRAFTSMAN V20 {search_term.title()}",
                "price": self._generate_realistic_price(item_type, "budget"),
                "rating": 4.2,
                "review_count": 654,
                "features": ["V20 MAX compatible", "LED light", "2-year warranty"],
                "availability": "Limited stock",
                "shipping": "Free shipping over $45"
            }
        ]
        
        for result in base_results:
            result["quality_score"] = self._calculate_quality_score(result)
            result["value_score"] = self._calculate_value_score(result)
        
        return base_results
    
    def _generate_amazon_results(self, search_term: str, item_type: str) -> List[Dict]:
        """Generate realistic Amazon search results"""
        base_results = [
            {
                "title": f"BLACK+DECKER {search_term.title()} - Amazon's Choice",
                "price": self._generate_realistic_price(item_type, "budget"),
                "rating": 4.0,
                "review_count": 2156,
                "features": ["Amazon's Choice", "Prime eligible", "30-day returns"],
                "availability": "In stock",
                "shipping": "FREE Prime delivery"
            }
        ]
        
        for result in base_results:
            result["quality_score"] = self._calculate_quality_score(result)
            result["value_score"] = self._calculate_value_score(result)
        
        return base_results
    
    def _generate_harbor_freight_results(self, search_term: str, item_type: str) -> List[Dict]:
        """Generate realistic Harbor Freight search results"""
        base_results = [
            {
                "title": f"BAUER {search_term.title()} - Value Line",
                "price": self._generate_realistic_price(item_type, "budget") * 0.7,  # Harbor Freight discount
                "rating": 3.8,
                "review_count": 445,
                "features": ["Budget-friendly", "90-day warranty", "Frequent sales"],
                "availability": "In stock",
                "shipping": "Store pickup available"
            }
        ]
        
        for result in base_results:
            result["quality_score"] = self._calculate_quality_score(result)
            result["value_score"] = self._calculate_value_score(result)
        
        return base_results
    
    def _generate_northern_tool_results(self, search_term: str, item_type: str) -> List[Dict]:
        """Generate realistic Northern Tool search results"""
        base_results = [
            {
                "title": f"Klutch {search_term.title()} - Heavy Duty",
                "price": self._generate_realistic_price(item_type, "professional"),
                "rating": 4.5,
                "review_count": 234,
                "features": ["Heavy duty", "Commercial grade", "2-year warranty"],
                "availability": "In stock",
                "shipping": "Freight shipping available"
            }
        ]
        
        for result in base_results:
            result["quality_score"] = self._calculate_quality_score(result)
            result["value_score"] = self._calculate_value_score(result)
        
        return base_results
    
    def _generate_realistic_price(self, item_type: str, tier: str) -> float:
        """Generate realistic pricing based on item type and quality tier"""
        category = "materials" if item_type == "material" else "power_tools" if "drill" in item_type.lower() or "saw" in item_type.lower() else "hand_tools"
        
        price_range = self.price_ranges.get(category, self.price_ranges["hand_tools"])
        min_price, max_price = price_range.get(tier, (20, 100))
        
        # Generate price within range with some randomness
        import random
        price = random.uniform(min_price, max_price)
        return round(price, 2)
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """Calculate quality score based on various factors"""
        score = 0.0
        
        # Rating contribution (40%)
        rating = result.get("rating", 3.0)
        score += (rating / 5.0) * 0.4
        
        # Review count contribution (20%)
        review_count = result.get("review_count", 0)
        if review_count > 1000:
            score += 0.2
        elif review_count > 500:
            score += 0.15
        elif review_count > 100:
            score += 0.1
        else:
            score += 0.05
        
        # Features quality analysis (40%)
        features = result.get("features", [])
        feature_score = 0.0
        for feature in features:
            feature_lower = feature.lower()
            if any(indicator in feature_lower for indicator in self.quality_indicators["excellent"]):
                feature_score += 0.15
            elif any(indicator in feature_lower for indicator in self.quality_indicators["very_good"]):
                feature_score += 0.1
            elif any(indicator in feature_lower for indicator in self.quality_indicators["good"]):
                feature_score += 0.05
        
        score += min(feature_score, 0.4)  # Cap at 40%
        
        return min(score, 1.0)  # Ensure score doesn't exceed 1.0
    
    def _calculate_value_score(self, result: Dict) -> float:
        """Calculate value score (quality vs price ratio)"""
        quality_score = result.get("quality_score", 0.5)
        price = result.get("price", 100)
        
        # Normalize price to 0-1 scale (assuming max reasonable price of $500)
        price_normalized = min(price / 500.0, 1.0)
        
        # Value score: high quality, low price = high value
        value_score = quality_score / (price_normalized + 0.1)  # Avoid division by zero
        
        return min(value_score, 1.0)
    
    def _get_top_recommendations(self, search_results: List[Dict]) -> List[Dict]:
        """Get top 3 recommendations based on value score"""
        if not search_results:
            return []
        
        # Sort by value score
        sorted_results = sorted(search_results, key=lambda x: x.get("value_score", 0), reverse=True)
        
        top_recommendations = []
        for i, result in enumerate(sorted_results[:3]):
            recommendation = result.copy()
            recommendation["rank"] = i + 1
            recommendation["recommendation_reason"] = self._generate_recommendation_reason(result, i)
            top_recommendations.append(recommendation)
        
        return top_recommendations
    
    def _generate_recommendation_reason(self, result: Dict, rank: int) -> str:
        """Generate explanation for why this product is recommended"""
        reasons = []
        
        if rank == 0:  # Best value
            reasons.append("Best overall value")
        elif rank == 1:  # Second choice
            reasons.append("Excellent alternative")
        else:  # Third choice
            reasons.append("Budget-friendly option")
        
        rating = result.get("rating", 0)
        if rating >= 4.3:
            reasons.append("highly rated")
        elif rating >= 4.0:
            reasons.append("well-reviewed")
        
        review_count = result.get("review_count", 0)
        if review_count > 1000:
            reasons.append("extensively tested by users")
        
        return ", ".join(reasons)
    
    def _analyze_prices(self, search_results: List[Dict]) -> Dict:
        """Analyze price range and distribution"""
        if not search_results:
            return {}
        
        prices = [result.get("price", 0) for result in search_results]
        
        return {
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "price_range": max(prices) - min(prices),
            "budget_options": len([p for p in prices if p < sum(prices) / len(prices) * 0.8]),
            "premium_options": len([p for p in prices if p > sum(prices) / len(prices) * 1.2])
        }
    
    def _analyze_quality(self, search_results: List[Dict]) -> Dict:
        """Analyze quality distribution"""
        if not search_results:
            return {}
        
        quality_scores = [result.get("quality_score", 0) for result in search_results]
        avg_rating = sum(result.get("rating", 0) for result in search_results) / len(search_results)
        
        return {
            "avg_quality_score": sum(quality_scores) / len(quality_scores),
            "avg_rating": avg_rating,
            "high_quality_options": len([q for q in quality_scores if q > 0.7]),
            "reliable_options": len([q for q in quality_scores if q > 0.5]),
            "quality_range": max(quality_scores) - min(quality_scores)
        }
    
    def _generate_shopping_guide(self, search_results: List[Dict]) -> Dict:
        """Generate comprehensive shopping guide"""
        if not search_results:
            return {}
        
        # Calculate overall statistics
        total_items = len(search_results)
        total_options = sum(len(item["search_results"]) for item in search_results)
        
        # Best retailers analysis
        retailer_counts = {}
        for item in search_results:
            for result in item["search_results"]:
                retailer = result.get("retailer", "Unknown")
                retailer_counts[retailer] = retailer_counts.get(retailer, 0) + 1
        
        best_retailers = sorted(retailer_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Money-saving tips
        money_saving_tips = [
            "Compare prices across multiple retailers before purchasing",
            "Look for bundle deals when buying multiple items",
            "Check for seasonal sales and clearance events",
            "Consider store brands for basic tools - often 30-50% cheaper",
            "Sign up for retailer newsletters to get exclusive discounts",
            "Use price tracking tools to monitor for price drops",
            "Check for open-box or display model discounts",
            "Consider buying used tools from reputable sellers"
        ]
        
        # Quality tips
        quality_tips = [
            "Read recent reviews, not just overall ratings",
            "Look for products with 4+ star ratings and 100+ reviews",
            "Check warranty terms - longer warranties usually indicate better quality",
            "Avoid the cheapest option unless budget is extremely tight",
            "Professional-grade tools are worth the investment for frequent use",
            "Consider the total cost of ownership, including replacement costs"
        ]
        
        return {
            "summary": {
                "total_items_searched": total_items,
                "total_options_found": total_options,
                "average_options_per_item": total_options / total_items if total_items > 0 else 0
            },
            "best_retailers": best_retailers[:3],
            "money_saving_tips": money_saving_tips,
            "quality_tips": quality_tips,
            "shopping_strategy": self._generate_shopping_strategy(search_results)
        }
    
    def _generate_shopping_strategy(self, search_results: List[Dict]) -> List[str]:
        """Generate personalized shopping strategy"""
        strategies = []
        
        # Analyze price sensitivity
        total_budget = sum(item["price_analysis"]["avg_price"] for item in search_results if "price_analysis" in item)
        
        if total_budget < 200:
            strategies.append("Focus on budget-friendly options from Harbor Freight and store brands")
            strategies.append("Consider buying the most essential tools first and upgrading later")
        elif total_budget < 500:
            strategies.append("Mix of mid-range and budget tools - invest more in frequently used items")
            strategies.append("Look for Home Depot or Lowes store brands for good value")
        else:
            strategies.append("Invest in professional-grade tools for long-term value")
            strategies.append("Consider tool systems from one brand for battery compatibility")
        
        strategies.append("Start with store pickup to avoid shipping costs")
        strategies.append("Time purchases around major sales events (Black Friday, spring sales)")
        
        return strategies
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input has items to search"""
        items = input_data.get("items")
        return items is not None and isinstance(items, list) and len(items) > 0