"""
配置管理
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 基本设置
    app_name: str = "DIY Agent System"
    debug: bool = False
    
    # API Keys
    openai_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    
    # 数据库
    database_url: str = "sqlite:///./diy_agent_system.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # 文件上传
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    
    # Agent配置
    max_concurrent_agents: int = 5
    agent_timeout: int = 300  # 5分钟
    
    # 搜索配置
    search_results_limit: int = 20
    quality_threshold: float = 3.5
    
    class Config:
        env_file = ".env"


# 全局设置实例
_settings = None


def get_settings() -> Settings:
    """获取设置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings