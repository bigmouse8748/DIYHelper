"""
Product Recommendation Agent
使用AI大模型推荐真实的工具和材料品牌型号
"""
import asyncio
from typing import List, Dict, Any, Optional
from core.agent_base import BaseAgent, AgentTask, AgentResult
import logging

logger = logging.getLogger(__name__)

class ProductRecommendationAgent(BaseAgent):
    """产品推荐智能体 - 使用AI推荐真实品牌和型号"""
    
    def __init__(self, name: str = "product_recommendation"):
        super().__init__(name)
        
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行产品推荐任务"""
        try:
            tools_and_materials = input_data.get("tools_and_materials", [])
            project_type = input_data.get("project_type", "woodworking")
            budget_level = input_data.get("budget_level", "medium")
            
            recommendations = []
            
            for item in tools_and_materials:
                item_name = item.get("name", "")
                item_type = item.get("type", "tool")  # tool or material
                
                # 使用AI推荐真实品牌和型号
                ai_recommendations = await self._get_ai_recommendations(
                    item_name, item_type, project_type, budget_level
                )
                
                # 搜索真实购物链接
                products = await self._search_products(ai_recommendations)
                
                recommendations.append({
                    "material": item_name,
                    "products": products,
                    "total_assessed": len(products),
                    "avg_quality_score": sum(p.get("quality_score", 4.0) for p in products) / len(products) if products else 4.0
                })
            
            return AgentResult(
                success=True,
                data={
                    "assessed_results": recommendations,
                    "overall_recommendations": self._generate_overall_recommendations(recommendations)
                }
            )
            
        except Exception as e:
            logger.error(f"Product recommendation error: {str(e)}")
            return AgentResult(success=False, error=str(e))
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        return "tools_and_materials" in input_data and isinstance(input_data["tools_and_materials"], list)
    
    async def _get_ai_recommendations(self, item_name: str, item_type: str, project_type: str, budget_level: str) -> List[Dict]:
        """使用AI获取工具/材料推荐"""
        
        # 构建AI查询prompt
        prompt = self._build_recommendation_prompt(item_name, item_type, project_type, budget_level)
        
        # TODO: 这里应该调用实际的LLM API (OpenAI, Anthropic, etc.)
        # ai_response = await self._query_llm(prompt)
        # recommendations = self._parse_ai_response(ai_response)
        
        # 目前使用增强的静态数据库模拟AI响应
        # 基于不同工具类型的智能推荐模板
        recommendations_db = {
            "Power Drill": [
                {
                    "brand": "DeWalt",
                    "model": "DCD771C2 20V MAX Cordless Drill",
                    "level": "professional",
                    "price_range": "$89-129",
                    "features": ["Brushless motor", "Long battery life", "Professional grade"]
                },
                {
                    "brand": "BLACK+DECKER",
                    "model": "LD120VA 20V MAX Cordless Drill",
                    "level": "entry",
                    "price_range": "$45-65",
                    "features": ["Good for beginners", "Affordable", "Reliable"]
                },
                {
                    "brand": "Milwaukee",
                    "model": "M18 FUEL 2804-20",
                    "level": "professional",
                    "price_range": "$149-199",
                    "features": ["High torque", "FUEL technology", "Long runtime"]
                }
            ],
            "Circular Saw": [
                {
                    "brand": "SKILSAW",
                    "model": "SPT67WL-01 15-Amp 7-1/4 In. Sidewinder",
                    "level": "professional", 
                    "price_range": "$179-229",
                    "features": ["Magnesium construction", "Lightweight", "Professional grade"]
                },
                {
                    "brand": "BLACK+DECKER",
                    "model": "BDECS300C 13-Amp 7-1/4-Inch Circular Saw",
                    "level": "entry",
                    "price_range": "$69-89",
                    "features": ["Entry level", "Good value", "Reliable performance"]
                }
            ],
            "Table Saw": [
                {
                    "brand": "SawStop",
                    "model": "PCS175-TGP236 1.75-HP Professional Cabinet Saw",
                    "level": "professional",
                    "price_range": "$2,199-2,799",
                    "features": ["Safety brake technology", "Professional grade", "Precise cuts"]
                },
                {
                    "brand": "DeWalt",
                    "model": "DWE7491RS 10-Inch Jobsite Table Saw",
                    "level": "intermediate",
                    "price_range": "$649-799",
                    "features": ["Portable", "Rolling stand", "Rack and pinion fence"]
                },
                {
                    "brand": "SKIL",
                    "model": "3410-02 10-Inch Table Saw",
                    "level": "entry",
                    "price_range": "$199-279",
                    "features": ["Budget-friendly", "Good for beginners", "Compact design"]
                }
            ],
            "Safety Glasses": [
                {
                    "brand": "3M",
                    "model": "SecureFit 400 Series SF401AF",
                    "level": "professional",
                    "price_range": "$8-15",
                    "features": ["Anti-fog coating", "ANSI Z87.1 certified", "Comfortable fit"]
                },
                {
                    "brand": "Uvex",
                    "model": "S3200 Genesis Safety Eyewear",
                    "level": "entry",
                    "price_range": "$5-12",
                    "features": ["Basic protection", "Affordable", "Clear vision"]
                }
            ]
        }
        
        # 材料推荐
        material_recommendations = {
            "Pine Wood Board": [
                {
                    "brand": "Select Pine",
                    "model": "Construction Grade Pine Board 3/4\" x 12\" x 8'",
                    "level": "standard",
                    "price_range": "$25-45",
                    "features": ["Good quality", "Standard grade", "Widely available"]
                }
            ],
            "Wood Screws": [
                {
                    "brand": "GRK Fasteners",
                    "model": "R4 Multi-Purpose Wood Screws",
                    "level": "professional",
                    "price_range": "$15-25",
                    "features": ["Self-drilling", "Premium quality", "Strong grip"]
                }
            ]
        }
        
        # 智能推荐算法：确保每个工具/材料都有准确的3个推荐
        all_recommendations = []
        
        # 先从数据库获取基础推荐
        if item_type == "tool":
            base_recommendations = recommendations_db.get(item_name, [])
        else:
            base_recommendations = material_recommendations.get(item_name, [])
            
        # 如果没有找到对应推荐，使用通用推荐逻辑
        if not base_recommendations:
            base_recommendations = await self._generate_generic_recommendations(item_name, item_type, project_type)
            
        # 基于预算级别和项目类型智能筛选推荐
        for rec in base_recommendations:
            rec = rec.copy()  # 避免修改原数据
            
            # AI智能调整：基于预算级别调整推荐优先级
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
            
            # AI智能调整：基于项目类型优化推荐
            if project_type == "woodworking" and any(word in item_name.lower() for word in ["drill", "saw", "wood", "clamp"]):
                rec["ai_priority"] *= 1.2  # 提升木工工具优先级
            elif project_type == "electronics" and any(word in item_name.lower() for word in ["safety", "wire", "solder"]):
                rec["ai_priority"] *= 1.1  # 提升电子项目安全设备优先级
                
            all_recommendations.append(rec)
            
        # 按AI优先级排序
        all_recommendations.sort(key=lambda x: x.get("ai_priority", 0.5), reverse=True)
        
        # 确保恰好返回3个推荐
        if len(all_recommendations) < 3:
            # 如果推荐不足3个，生成额外的推荐
            additional_recs = await self._generate_additional_recommendations(
                item_name, item_type, project_type, budget_level, 3 - len(all_recommendations)
            )
            all_recommendations.extend(additional_recs)
        
        return all_recommendations[:3]  # 确保恰好3个
    
    def _build_recommendation_prompt(self, item_name: str, item_type: str, project_type: str, budget_level: str) -> str:
        """构建AI推荐查询prompt"""
        return f"""
        作为专业的DIY工具推荐专家，请为以下项目推荐最适合的{item_type}：

        项目类型：{project_type}
        需要的{item_type}：{item_name}  
        预算级别：{budget_level}

        请推荐：
        1. 入门级选择（性价比最高）
        2. 中级选择（平衡性能和价格）
        3. 专业级选择（最高性能）

        对于每个推荐，请提供：
        - 品牌和具体型号
        - 主要特点和优势
        - 大概价格范围
        - 适用场景

        重点考虑：
        - 在美国市场的可获得性
        - 主要零售商（Home Depot, Lowes, Amazon, Walmart）的销售情况
        - 用户评价和可靠性
        - 对于{project_type}项目的适用性
        """
    
    async def _query_llm(self, prompt: str) -> str:
        """查询大语言模型（模拟实现）"""
        # 这里应该是实际的LLM API调用
        # 例如：
        # import openai
        # response = await openai.ChatCompletion.acreate(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content
        
        # 暂时返回模拟响应
        return "AI模拟响应：基于项目分析，推荐以下工具..."
    
    def _parse_ai_response(self, ai_response: str) -> List[Dict]:
        """解析AI响应为结构化推荐数据"""
        # 这里应该解析实际的AI响应
        # 目前返回空列表，让系统使用静态数据库
        return []
    
    async def _generate_generic_recommendations(self, item_name: str, item_type: str, project_type: str) -> List[Dict]:
        """为未知工具/材料生成通用推荐"""
        # 基于工具/材料名称的智能匹配
        generic_recommendations = []
        
        # 常见工具品牌映射
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
        
        # 材料品牌映射
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
        
        # 智能匹配关键词
        for keyword, recommendations in (tool_brands if item_type == "tool" else material_brands).items():
            if keyword.lower() in item_name.lower():
                return recommendations[:3]
        
        # 如果没有匹配，生成默认推荐
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
        """生成额外的推荐以确保达到3个"""
        additional_recs = []
        
        # 备选品牌列表
        backup_brands = {
            "tool": ["Ridgid", "Ryobi", "Porter-Cable", "Bosch", "Makita"],
            "material": ["Simpson Strong-Tie", "Titebond", "3M", "Gorilla", "Loctite"]
        }
        
        brands = backup_brands.get(item_type, ["Generic Brand"])
        levels = ["entry", "intermediate", "professional"]
        
        for i in range(count_needed):
            brand = brands[i % len(brands)]
            level = levels[i % len(levels)]
            
            # 价格范围基于级别
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
                "ai_priority": 0.4 - (i * 0.1)  # 降低优先级，因为这是备用推荐
            })
        
        return additional_recs
    
    async def _search_products(self, ai_recommendations: List[Dict]) -> List[Dict]:
        """基于AI推荐搜索真实产品链接"""
        products = []
        
        # 美国主要零售商的真实产品链接策略
        retailers = [
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
            }
        ]
        
        for i, recommendation in enumerate(ai_recommendations):
            retailer = retailers[i % len(retailers)]
            
            # 构建更真实的搜索词
            brand = recommendation['brand'].replace(" ", "+")
            model_key = recommendation['model'].split(" - ")[0]  # 取型号的主要部分
            search_term = f"{brand}+{model_key}".replace(" ", "+")
            
            # 生成更直接的购物链接
            direct_url = retailer['search_url'].format(search_term)
            
            product = {
                "title": f"{recommendation['brand']} {recommendation['model']}",
                "price": recommendation['price_range'].split('-')[0].strip() if '-' in recommendation['price_range'] else recommendation['price_range'],
                "image_url": self._get_relevant_product_image(recommendation, retailer['name']),
                "product_url": direct_url,
                "platform": retailer['name'],
                "rating": self._calculate_rating(recommendation),
                "quality_score": self._calculate_quality_score(recommendation),
                "quality_reasons": recommendation.get('features', [f"Good {recommendation['level']} choice", "Reliable brand", "Available online"])[:3],
                "price_value_ratio": self._calculate_value_ratio(recommendation),
                "recommendation_level": self._get_recommendation_level(recommendation['level'])
            }
            
            products.append(product)
        
        return products
    
    def _get_relevant_product_image(self, recommendation: Dict, retailer_name: str) -> str:
        """获取与产品相关的图片URL"""
        # 基于产品类型和品牌的智能图片映射
        brand = recommendation.get('brand', '').lower()
        model = recommendation.get('model', '').lower()
        
        # 工具类型映射
        tool_images = {
            'drill': "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop",
            'saw': "https://images.unsplash.com/photo-1609592067508-0e2120ac7fe7?w=400&h=300&fit=crop",
            'hammer': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
            'safety': "https://images.unsplash.com/photo-1577962917302-cd874c99b6d3?w=400&h=300&fit=crop",
            'screw': "https://images.unsplash.com/photo-1609592067508-0e2120ac7fe7?w=400&h=300&fit=crop",
            'wood': "https://images.unsplash.com/photo-1541123437800-1bb1317badc2?w=400&h=300&fit=crop",
            'glue': "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400&h=300&fit=crop",
            'sandpaper': "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=400&h=300&fit=crop"
        }
        
        # 品牌特定映射
        brand_images = {
            'dewalt': "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop",
            'black+decker': "https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=400&h=300&fit=crop",
            'milwaukee': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
            'stanley': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
            '3m': "https://images.unsplash.com/photo-1577962917302-cd874c99b6d3?w=400&h=300&fit=crop"
        }
        
        # 首先检查品牌特定图片
        if brand in brand_images:
            return brand_images[brand]
            
        # 然后基于产品类型匹配
        for tool_type, image_url in tool_images.items():
            if tool_type in model or tool_type in brand:
                return image_url
        
        # 默认返回通用工具图片
        return "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop"
    
    def _calculate_rating(self, recommendation: Dict) -> float:
        """基于推荐等级计算评分"""
        level_ratings = {
            "professional": 4.6,
            "intermediate": 4.3,
            "entry": 4.0,
            "standard": 4.2
        }
        return level_ratings.get(recommendation['level'], 4.0)
    
    def _calculate_quality_score(self, recommendation: Dict) -> float:
        """计算质量评分"""
        level_scores = {
            "professional": 4.8,
            "intermediate": 4.4,
            "entry": 4.0,
            "standard": 4.2
        }
        return level_scores.get(recommendation['level'], 4.0)
    
    def _calculate_value_ratio(self, recommendation: Dict) -> float:
        """计算性价比评分"""
        level_values = {
            "professional": 4.2,
            "intermediate": 4.5,
            "entry": 4.7,
            "standard": 4.3
        }
        return level_values.get(recommendation['level'], 4.0)
    
    def _get_recommendation_level(self, level: str) -> str:
        """获取推荐等级标签"""
        level_labels = {
            "professional": "Professional Choice",
            "intermediate": "Highly Recommended", 
            "entry": "Best Value",
            "standard": "Good Choice"
        }
        return level_labels.get(level, "Recommended")
    
    def _generate_overall_recommendations(self, recommendations: List[Dict]) -> Dict:
        """生成总体推荐信息"""
        total_products = sum(rec['total_assessed'] for rec in recommendations)
        avg_score = sum(rec['avg_quality_score'] for rec in recommendations) / len(recommendations) if recommendations else 4.0
        
        # 获取最佳产品推荐
        best_products = []
        for rec in recommendations[:2]:  # 取前2个类别
            if rec['products']:
                best_product = max(rec['products'], key=lambda p: p['quality_score'])
                best_products.append({
                    "material": rec['material'],
                    "product": {
                        "title": best_product['title'],
                        "platform": best_product['platform'],
                        "product_url": best_product['product_url']
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
                "Check for manufacturer warranties and return policies"
            ],
            "quality_distribution": {
                "Professional Choice": 0,
                "Highly Recommended": 0,
                "Best Value": 0,
                "Good Choice": 0
            }
        }