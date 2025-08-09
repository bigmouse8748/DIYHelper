# DIY Agent System

基于AI Agent架构的智能DIY项目分析平台

## 🚀 功能特性

- **智能图像分析**: 使用OpenAI GPT-4 Vision API分析DIY项目图片
- **智能商品搜索**: 多平台商品搜索（淘宝、京东、1688等）
- **质量智能评估**: 基于多维度评估算法评估产品质量和性价比
- **Agent协作架构**: 模块化Agent设计，支持扩展和定制
- **现代化界面**: Vue3 + TypeScript + Element Plus构建的响应式界面

## 🏗️ 系统架构

```
Frontend (Vue3 + TS) 
    ↓
API Gateway (FastAPI)
    ↓
Agent Manager
    ↓
┌─────────────────────────────────────┐
│  Specialized Agents                 │
│  ┌──────────────┐ ┌──────────────┐ │
│  │ Image        │ │ Product      │ │
│  │ Analysis     │ │ Search       │ │
│  │ Agent        │ │ Agent        │ │
│  └──────────────┘ └──────────────┘ │
│                                     │
│  ┌──────────────┐                  │
│  │ Quality      │                  │
│  │ Assessment   │                  │
│  │ Agent        │                  │
│  └──────────────┘                  │
└─────────────────────────────────────┘
```

## 📋 环境要求

- **Python**: 3.11+
- **Node.js**: 18+
- **Chrome Browser**: 用于Selenium网页抓取
- **OpenAI API Key**: 用于图像分析

## 🛠️ 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd diy-agent-system
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate
# 或 (macOS/Linux)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加必要的API密钥
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 环境变量配置

在 `backend/.env` 文件中配置：

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
DEBUG=True
PORT=8000
```

### 5. 启动应用

**启动后端:**
```bash
cd backend
python start.py
```

**启动前端:**
```bash
cd frontend  
npm run dev
```

应用将在以下地址访问：
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🐳 Docker部署

### 使用Docker Compose

```bash
# 配置环境变量
cp backend/.env.example backend/.env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 单独构建

**后端:**
```bash
cd backend
docker build -t diy-agent-backend .
docker run -p 8000:8000 --env-file .env diy-agent-backend
```

**前端:**
```bash
cd frontend
docker build -t diy-agent-frontend .
docker run -p 3000:80 diy-agent-frontend
```

## 📖 API使用说明

### 分析项目

```bash
curl -X POST "http://localhost:8000/analyze-project" \
  -H "Content-Type: multipart/form-data" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "description=木工桌子制作" \
  -F "project_type=woodworking" \
  -F "budget_range=300-500"
```

### 单独执行Agent

```bash
curl -X POST "http://localhost:8000/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "product_search",
    "input_data": {
      "materials": ["木板", "螺丝", "胶水"]
    }
  }'
```

### 获取Agent状态

```bash
curl "http://localhost:8000/agents/status"
```

## 🔧 Agent开发

### 创建新Agent

1. 在 `backend/agents/` 下创建新目录
2. 实现Agent类继承 `BaseAgent`
3. 在 `agents/__init__.py` 中注册

```python
from core import BaseAgent, AgentResult
from typing import Dict, Any

class MyCustomAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("my_custom_agent", config)
        
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        # 验证输入数据
        return True
        
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        # 实现Agent逻辑
        return AgentResult(
            success=True,
            data={"result": "success"}
        )
```

## 📁 项目结构

```
diy-agent-system/
├── backend/                 # FastAPI后端
│   ├── agents/             # Agent实现
│   │   ├── image_analysis/ # 图像分析Agent
│   │   ├── product_search/ # 商品搜索Agent
│   │   └── quality_assessment/ # 质量评估Agent
│   ├── api/               # API路由
│   ├── core/              # 核心框架
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
├── frontend/               # Vue3前端
│   ├── src/
│   │   ├── components/    # 公共组件
│   │   ├── views/         # 页面组件
│   │   ├── api/           # API调用
│   │   ├── types/         # TypeScript类型
│   │   └── styles/        # 样式文件
│   └── public/
└── docker-compose.yml     # Docker编排
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交修改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交Pull Request

## 📝 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🐛 问题反馈

如果您遇到任何问题，请在 [Issues](https://github.com/your-repo/issues) 中提交

## 📞 联系方式

- Email: support@diy-helper.com
- GitHub: [项目地址]

---

**注意**: 本项目需要OpenAI API密钥才能正常运行图像分析功能。请确保在使用前正确配置环境变量。