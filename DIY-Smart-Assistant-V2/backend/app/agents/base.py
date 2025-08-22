"""
Base Agent Classes and Interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio
import logging
import uuid
import time

logger = logging.getLogger(__name__)


class AgentTask(BaseModel):
    """Agent task model"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    input_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentResult(BaseModel):
    """Agent execution result"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """Base Agent class for all AI agents"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.is_running = False
        self.tasks_completed = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute agent task - to be implemented by subclasses"""
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data - can be overridden by subclasses"""
        return input_data is not None and isinstance(input_data, dict)
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process a task with error handling and timing"""
        start_time = time.time()
        
        try:
            # Validate input
            if not self.validate_input(task.input_data):
                raise ValueError("Invalid input data")
            
            self.is_running = True
            task.status = "running"
            logger.info(f"Agent {self.name} processing task {task.task_id}")
            
            # Execute task
            result = await self.execute(task.input_data)
            
            # Update statistics
            execution_time = time.time() - start_time
            self.tasks_completed += 1
            self.total_execution_time += execution_time
            self.last_execution = datetime.utcnow()
            
            result.execution_time = execution_time
            task.status = "completed"
            task.result = result.data
            
            logger.info(f"Agent {self.name} completed task {task.task_id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Agent {self.name} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            task.status = "failed"
            task.error = str(e)
            
            return AgentResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                metadata={"task_id": task.task_id}
            )
        finally:
            self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "tasks_completed": self.tasks_completed,
            "total_execution_time": round(self.total_execution_time, 2),
            "average_execution_time": round(
                self.total_execution_time / max(1, self.tasks_completed), 2
            ),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "config": self.config
        }
    
    def reset_stats(self):
        """Reset agent statistics"""
        self.tasks_completed = 0
        self.total_execution_time = 0.0
        self.last_execution = None


class AgentManager:
    """Manager for multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_history: List[AgentTask] = []
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the manager"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    async def execute_task(self, agent_name: str, input_data: Dict[str, Any]) -> AgentResult:
        """Execute a task using specified agent"""
        agent = self.get_agent(agent_name)
        if not agent:
            return AgentResult(
                success=False,
                error=f"Agent '{agent_name}' not found"
            )
        
        task = AgentTask(
            agent_name=agent_name,
            input_data=input_data
        )
        
        self.task_history.append(task)
        result = await agent.process_task(task)
        
        return result
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        return {
            name: agent.get_status() 
            for name, agent in self.agents.items()
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task history"""
        recent_tasks = self.task_history[-limit:] if limit > 0 else self.task_history
        return [
            {
                "task_id": task.task_id,
                "agent_name": task.agent_name,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "has_result": task.result is not None,
                "has_error": task.error is not None
            }
            for task in recent_tasks
        ]


# Global agent manager instance
agent_manager = AgentManager()