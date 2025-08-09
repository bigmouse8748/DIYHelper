"""
DIY Agent System FastAPI 简化版主应用
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

# 导入核心模块
from core import agent_manager
from utils.config import get_settings
from agents.product_recommendation_agent import ProductRecommendationAgent

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="DIY Agent System",
    description="智能DIY项目分析和购物助手",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # Vue开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据模型
class AgentExecuteRequest(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]


# 主要API端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "DIY Agent System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/analyze-project")
async def analyze_project(
    images: List[UploadFile] = File(...),
    description: str = Form(default=""),
    project_type: str = Form(default=""),
    budget_range: str = Form(default="")
):
    """分析DIY项目"""
    try:
        # 初始化返回结果
        mock_result = {"success": False, "error": "Processing failed", "results": []}
        
        # 保存上传的图片
        image_paths = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        for image in images:
            file_path = os.path.join(upload_dir, image.filename)
            with open(file_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            image_paths.append(file_path)
        
        # 构建项目分析数据
        analysis_data = {
            "project_name": "DIY Wooden Table Project",
            "description": f"Based on analysis of {len(images)} uploaded images, this is a {project_type or 'woodworking'} DIY project. {description}",
            "materials": [
                {"name": "Pine Wood Board", "specification": "3/4 inch thick", "quantity": "2 pieces", "estimated_price_range": "$25-40"},
                {"name": "Wood Screws", "specification": "1.5 inch long", "quantity": "20 pieces", "estimated_price_range": "$3-5"},
                {"name": "Wood Glue", "specification": "Strong adhesive", "quantity": "1 bottle", "estimated_price_range": "$4-8"},
                {"name": "Wood Stain", "specification": "Natural finish", "quantity": "1 can", "estimated_price_range": "$8-12"},
                {"name": "Sandpaper", "specification": "120/220 grit", "quantity": "5 sheets", "estimated_price_range": "$5-10"}
            ],
            "tools": [
                {"name": "Power Drill", "necessity": "Essential"},
                {"name": "Screwdriver Set", "necessity": "Essential"}, 
                {"name": "Measuring Tape", "necessity": "Essential"},
                {"name": "Saw (Circular/Miter)", "necessity": "Essential"},
                {"name": "Sandpaper/Sander", "necessity": "Essential"},
                {"name": "Safety Glasses", "necessity": "Essential"},
                {"name": "Work Gloves", "necessity": "Recommended"},
                {"name": "Clamps", "necessity": "Recommended"},
                {"name": "Level", "necessity": "Recommended"}
            ],
            "difficulty_level": "medium",
            "estimated_time": "4-6 hours",
            "safety_notes": ["Wear safety glasses at all times", "Use tools safely and follow manufacturer instructions", "Keep workspace clean and well-organized", "Ensure adequate ventilation when using stains or adhesives"],
            "steps": [
                "1. Safety First: Put on safety glasses and work gloves. Ensure your workspace is well-ventilated and clean.",
                "2. Measure and Plan: Using measuring tape, carefully measure and mark all cut lines on the wood boards. Double-check all measurements.",
                "3. Cut the Wood: Use a circular saw or miter saw to cut the wood pieces according to your measurements. Sand cut edges smooth.",
                "4. Pre-drill Holes: Use the power drill to pre-drill pilot holes for screws to prevent wood splitting.",
                "5. Apply Wood Glue: Apply a thin, even layer of wood glue to joining surfaces. Work quickly as glue sets fast.",
                "6. Assemble Frame: Clamp pieces together and secure with wood screws. Use level to ensure everything is square.",
                "7. Initial Sanding: Sand all surfaces starting with 120-grit, then 220-grit sandpaper for smooth finish.",
                "8. Clean Surface: Remove all dust with tack cloth or compressed air before staining.",
                "9. Apply Stain: Use brush or cloth to apply wood stain evenly. Work with the grain, not against it.",
                "10. Final Assembly: Once stain is dry, complete any final assembly and add any hardware or accessories.",
                "11. Quality Check: Inspect all joints, sand any rough spots, and ensure the project is sturdy and safe to use."
            ]
        }
        
        # 使用智能推荐Agent生成产品推荐
        try:
            logger.info("Starting product recommendations generation")
            logger.info(f"Analysis data has {len(analysis_data.get('tools', []))} tools and {len(analysis_data.get('materials', []))} materials")
            product_recommendations = await generate_smart_product_recommendations(analysis_data, project_type, budget_range)
            logger.info(f"Product recommendations generated: {len(product_recommendations.get('assessed_results', []))} categories")
            for rec in product_recommendations.get('assessed_results', []):
                logger.info(f"  - {rec['material']}: {len(rec['products'])} products")
        except Exception as rec_error:
            logger.error(f"Product recommendation failed: {str(rec_error)}")
            # Use fallback recommendations
            product_recommendations = get_fallback_recommendations()
        
        # 构建最终结果
        mock_result = {
            "success": True,
            "results": [
                {
                    "data": {
                        "comprehensive_analysis": analysis_data,
                        "materials": [
                            {"name": "Pine Wood Board", "specification": "3/4 inch thick", "quantity": "2 pieces"},
                            {"name": "Wood Screws", "specification": "1.5 inch long", "quantity": "20 pieces"},
                            {"name": "Wood Glue", "specification": "Strong adhesive", "quantity": "1 bottle"}
                        ]
                    },
                    "execution_time": 2.5
                },
                {
                    "data": product_recommendations,
                    "execution_time": 1.8
                }
            ]
        }
        
        # 清理临时文件
        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)
        
        return mock_result
        
    except Exception as e:
        logger.error(f"Error analyzing project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_smart_product_recommendations(analysis_data: Dict, project_type: str, budget_range: str) -> Dict:
    """生成智能产品推荐"""
    try:
        # 创建ProductRecommendationAgent实例
        agent = ProductRecommendationAgent()
        
        # 准备工具和材料数据
        tools_and_materials = []
        
        # 从分析数据中提取工具和材料
        if "tools" in analysis_data:
            for tool in analysis_data["tools"]:
                tools_and_materials.append({
                    "name": tool["name"], 
                    "type": "tool",
                    "necessity": tool.get("necessity", "Recommended")
                })
                
        if "materials" in analysis_data:
            for material in analysis_data["materials"]: 
                tools_and_materials.append({
                    "name": material["name"],
                    "type": "material", 
                    "specification": material.get("specification", "")
                })
        
        # 创建agent任务
        from core.agent_base import AgentTask
        from datetime import datetime
        task = AgentTask(
            task_id=f"recommendation_{hash(str(analysis_data))}",
            agent_name="product_recommendation",
            input_data={
                "tools_and_materials": tools_and_materials,
                "project_type": project_type,
                "budget_level": budget_range
            },
            created_at=datetime.now()
        )
        
        # 执行推荐任务
        result = await agent.process_task(task)
        
        if result.success:
            return result.data
        else:
            logger.error(f"Agent recommendation failed: {result.error}")
            return get_fallback_recommendations()
            
    except Exception as e:
        logger.error(f"Error generating smart recommendations: {str(e)}")
        return get_fallback_recommendations()


def get_fallback_recommendations() -> Dict:
    """获取后备推荐数据"""
    return {
        "assessed_results": [
            {
                "material": "Power Drill",
                "products": [
                    {
                        "title": "BLACK+DECKER 20V MAX Cordless Drill",
                        "price": "$49.99",
                        "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop",
                        "product_url": "https://www.amazon.com/BLACK-DECKER-LD120VA-20-Volt-Lithium-Ion/dp/B00AXTBSRU",
                        "platform": "Amazon",
                        "rating": 4.4,
                        "quality_score": 4.3,
                        "quality_reasons": ["Great for beginners", "Good battery life", "Trusted brand"],
                        "price_value_ratio": 4.5,
                        "recommendation_level": "Best Value"
                    }
                ],
                "total_assessed": 1,
                "avg_quality_score": 4.3
            }
        ],
        "overall_recommendations": {
            "total_products_assessed": 1,
            "average_quality_score": 4.3,
            "best_products": [
                {
                    "material": "Power Drill",
                    "product": {
                        "title": "BLACK+DECKER 20V MAX Cordless Drill",
                        "platform": "Amazon", 
                        "product_url": "https://www.amazon.com/dp/B00AXTBSRU"
                    }
                }
            ],
            "shopping_tips": [
                "Choose products with 4.0+ star ratings for best quality",
                "Compare prices across multiple retailers",
                "Read customer reviews for insights"
            ],
            "quality_distribution": {
                "Best Value": 1
            }
        }
    }


@app.post("/agent/execute")
async def execute_agent(request: AgentExecuteRequest):
    """执行单个Agent"""
    try:
        # 模拟Agent执行
        return {
            "success": True,
            "data": {"message": f"Agent {request.agent_name} executed successfully (mock)"},
            "execution_time": 1.0
        }
    except Exception as e:
        logger.error(f"Error executing agent {request.agent_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test")
async def test_api():
    """API测试端点"""
    return {
        "message": "API连接正常",
        "status": "success",
        "timestamp": "2025-08-08T20:29:00Z"
    }


@app.get("/agents/status")
async def get_agents_status():
    """获取所有Agent状态"""
    return {
        "agents": {
            "image_analysis": {
                "name": "image_analysis",
                "is_running": False,
                "tasks_completed": 0,
                "config": {}
            },
            "product_search": {
                "name": "product_search", 
                "is_running": False,
                "tasks_completed": 0,
                "config": {}
            },
            "quality_assessment": {
                "name": "quality_assessment",
                "is_running": False,
                "tasks_completed": 0,
                "config": {}
            }
        },
        "total_agents": 3,
        "running_agents": 0
    }


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Starting DIY Agent System...")
    logger.info("Running in demo mode with mock data")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down DIY Agent System...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )