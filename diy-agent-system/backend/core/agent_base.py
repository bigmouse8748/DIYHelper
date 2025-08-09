"""
Agent基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


class AgentTask(BaseModel):
    """Agent任务模型"""
    task_id: str
    agent_name: str
    input_data: Dict[str, Any]
    created_at: datetime
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentResult(BaseModel):
    """Agent执行结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.is_running = False
        self.tasks_completed = 0
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """执行Agent任务"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        pass
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """处理任务"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 验证输入
            if not self.validate_input(task.input_data):
                raise ValueError("Invalid input data")
            
            self.is_running = True
            logger.info(f"Agent {self.name} processing task {task.task_id}")
            
            # 执行任务
            result = await self.execute(task.input_data)
            
            # 更新统计
            self.tasks_completed += 1
            execution_time = asyncio.get_event_loop().time() - start_time
            result.execution_time = execution_time
            
            logger.info(f"Agent {self.name} completed task {task.task_id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Agent {self.name} failed: {str(e)}"
            logger.error(error_msg)
            
            return AgentResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
        finally:
            self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "tasks_completed": self.tasks_completed,
            "config": self.config
        }


class AgentManager:
    """Agent管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.task_results: Dict[str, AgentResult] = {}
        
    def register_agent(self, agent: BaseAgent):
        """注册Agent"""
        self.agents[agent.name] = agent
        logger.info(f"Agent {agent.name} registered")
    
    def unregister_agent(self, agent_name: str):
        """注销Agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Agent {agent_name} unregistered")
    
    async def execute_task(self, agent_name: str, input_data: Dict[str, Any]) -> AgentResult:
        """执行单个任务"""
        if agent_name not in self.agents:
            return AgentResult(
                success=False,
                error=f"Agent {agent_name} not found"
            )
        
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            agent_name=agent_name,
            input_data=input_data,
            created_at=datetime.now()
        )
        
        agent = self.agents[agent_name]
        result = await agent.process_task(task)
        
        # 保存结果
        self.task_results[task.task_id] = result
        
        return result
    
    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[AgentResult]:
        """执行工作流（多个Agent协作）"""
        results = []
        context = {}  # 用于在Agent之间传递数据
        
        for step in workflow:
            agent_name = step.get("agent")
            input_data = step.get("input", {})
            
            # 将上下文数据合并到输入中
            input_data.update({"context": context})
            
            result = await self.execute_task(agent_name, input_data)
            results.append(result)
            
            # 更新上下文
            if result.success and result.data:
                context.update(result.data)
            else:
                # 如果某个步骤失败，停止工作流
                logger.error(f"Workflow stopped at step {agent_name}: {result.error}")
                break
                
        return results
    
    def get_agent_status(self, agent_name: str = None) -> Dict[str, Any]:
        """获取Agent状态"""
        if agent_name:
            if agent_name in self.agents:
                return self.agents[agent_name].get_status()
            else:
                return {"error": f"Agent {agent_name} not found"}
        else:
            return {
                "agents": {name: agent.get_status() for name, agent in self.agents.items()},
                "total_agents": len(self.agents),
                "running_agents": len([a for a in self.agents.values() if a.is_running])
            }


# 全局Agent管理器实例
agent_manager = AgentManager()