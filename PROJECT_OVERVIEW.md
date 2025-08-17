# DIY Smart Assistant - 项目概览和技术文档

## 项目简介

**DIY Smart Assistant** 是一个基于AI的智能DIY项目分析平台，结合Vue.js前端、FastAPI后端和AI Agent架构。系统能够分析上传的项目图片，提供材料清单、工具推荐、安全注意事项、构建步骤和智能购物建议。

## 技术栈

### 前端技术
- **Vue 3** (Composition API)
- **TypeScript** (类型安全)
- **Element Plus** (UI组件库)
- **Vue I18n** (国际化支持 - 中英双语)
- **Vite** (构建工具)
- **Axios** (HTTP客户端)
- **Vue Router** (路由管理)

### 后端技术
- **FastAPI** (Python异步Web框架)
- **Python 3.11+**
- **SQLAlchemy** (ORM)
- **SQLite** (数据库)
- **Pydantic** (数据验证)
- **JWT** (用户认证)
- **OpenAI API** (AI分析集成)
- **Uvicorn** (ASGI服务器)

### AI Agent架构
- **BaseAgent** 抽象基类
- **ProductRecommendationAgent** (产品推荐)
- **ProductInfoAgent** (产品信息提取)
- **ToolIdentificationAgent** (工具识别)

## 项目结构

```
F:/DIYList/
├── CLAUDE.md                                # Claude开发指南
├── PROJECT_OVERVIEW.md                     # 本文档
├── diy-agent-system/                       # 核心项目目录
│   ├── backend/                            # 后端目录
│   │   ├── agents/                         # AI Agent模块
│   │   │   ├── __init__.py
│   │   │   ├── product_info_agent.py      # 产品信息提取Agent
│   │   │   ├── product_recommendation_agent.py # 产品推荐Agent
│   │   │   └── tool_identification_agent.py # 工具识别Agent
│   │   ├── auth/                          # 认证模块
│   │   │   ├── __init__.py
│   │   │   └── auth_handler.py           # JWT认证处理
│   │   ├── core/                         # 核心模块
│   │   │   ├── __init__.py
│   │   │   └── agent_base.py            # Agent基类
│   │   ├── models/                       # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── product_models.py        # 产品模型
│   │   │   ├── tool_models.py           # 工具模型
│   │   │   └── user_models.py           # 用户模型
│   │   ├── services/                     # 业务服务
│   │   │   ├── openai_vision_service.py # OpenAI视觉服务
│   │   │   ├── price_scraper.py         # 价格爬虫服务
│   │   │   ├── product_scraper.py       # 产品爬虫服务
│   │   │   ├── product_service.py       # 产品业务服务
│   │   │   └── user_service.py          # 用户业务服务
│   │   ├── utils/                        # 工具类
│   │   │   ├── __init__.py
│   │   │   └── config.py                # 配置管理
│   │   ├── uploads/                      # 上传文件目录
│   │   │   └── products/                # 产品图片
│   │   ├── main_enhanced.py              # 增强版主应用 (当前使用)
│   │   ├── main_simple.py               # 简化版主应用
│   │   ├── database.py                  # 数据库配置
│   │   ├── diy_assistant.db             # 主数据库 (重要!)
│   │   ├── diy_system.db                # 系统数据库 (重要!)
│   │   ├── requirements.txt             # Python依赖
│   │   └── pyproject.toml              # Python项目配置
│   └── frontend/                        # 前端目录
│       ├── src/
│       │   ├── api/                     # API接口层
│       │   │   ├── analysis.ts          # 分析API
│       │   │   └── toolIdentification.ts # 工具识别API
│       │   ├── components/              # Vue组件
│       │   │   ├── AnalysisResults.vue  # 分析结果组件
│       │   │   └── LanguageSwitcher.vue # 语言切换组件
│       │   ├── views/                   # 页面组件
│       │   │   ├── AdminProductManagement.vue # 产品管理页面
│       │   │   ├── AdminUserManagement.vue    # 用户管理页面
│       │   │   ├── DIYAssistant.vue          # DIY助手页面
│       │   │   ├── Home.vue                  # 首页
│       │   │   ├── Login.vue                 # 登录页面
│       │   │   ├── ProductRecommendations.vue # 产品推荐页面
│       │   │   └── ToolIdentification.vue    # 工具识别页面
│       │   ├── locales/                 # 国际化文件
│       │   │   ├── en.ts               # 英文翻译
│       │   │   └── zh.ts               # 中文翻译
│       │   ├── stores/                  # 状态管理
│       │   │   └── auth.ts             # 认证状态
│       │   ├── router/                  # 路由配置
│       │   │   └── index.ts
│       │   ├── types/                   # TypeScript类型定义
│       │   │   └── index.ts
│       │   ├── App.vue                  # 根组件
│       │   └── main.ts                  # 入口文件
│       ├── package.json                 # 前端依赖配置
│       ├── vite.config.ts              # Vite配置
│       └── tsconfig.json               # TypeScript配置
```

## 核心功能模块

### 1. 用户认证系统
- **JWT Token认证**
- **管理员权限控制**
- **用户注册/登录**
- **密码加密存储**

**关键文件:**
- `backend/auth/auth_handler.py` - JWT处理
- `backend/models/user_models.py` - 用户模型
- `frontend/src/stores/auth.ts` - 前端认证状态

### 2. AI Agent系统
- **BaseAgent抽象类** - 所有Agent的基类
- **ProductRecommendationAgent** - 产品推荐和质量评估
- **ProductInfoAgent** - 从URL提取产品信息
- **ToolIdentificationAgent** - 工具识别和分类

**关键文件:**
- `backend/core/agent_base.py` - Agent基类
- `backend/agents/` - 所有Agent实现

### 3. 产品管理系统
- **AI驱动的URL产品信息提取**
- **产品数据管理**
- **图片上传和处理**
- **价格和商家信息管理**

**关键文件:**
- `backend/models/product_models.py` - 产品数据模型
- `backend/services/product_service.py` - 产品业务逻辑
- `frontend/src/views/AdminProductManagement.vue` - 产品管理界面

### 4. 项目分析系统
- **图像上传和分析**
- **材料清单生成**
- **工具推荐**
- **建设步骤生成**
- **安全注意事项**

**关键文件:**
- `backend/main_enhanced.py:analyze_project` - 项目分析端点
- `frontend/src/views/DIYAssistant.vue` - 分析界面

## 数据库架构

### 数据库文件
1. **diy_assistant.db** - 主数据库，包含用户、产品、项目等核心数据
2. **diy_system.db** - 系统数据库，包含配置和元数据

### 主要数据表
- **users** - 用户信息和权限
- **products** - 产品信息和推荐数据
- **projects** - DIY项目分析结果
- **tools** - 工具信息和分类

## 环境配置

### 后端环境变量
需要在 `backend/.env` 文件中配置：
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:///./diy_assistant.db
```

### 端口配置
- **后端端口:** 8002 (main_enhanced.py)
- **前端端口:** 3003 (自动分配，可能是3000-3003)

### CORS配置
后端允许的前端源：
- http://localhost:3000
- http://localhost:3001
- http://localhost:3002
- http://localhost:3003
- http://localhost:5173

## 运行方式

### 启动后端
```bash
cd diy-agent-system/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main_enhanced.py
```

### 启动前端
```bash
cd diy-agent-system/frontend
npm install
npm run dev
```

### 管理员账户
- **用户名:** admin
- **密码:** admin123

## API端点概览

### 认证端点
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册

### 项目分析端点
- `POST /analyze-project` - 分析DIY项目
- `GET /agents/status` - 获取Agent状态

### 管理员端点
- `GET /api/admin/users` - 获取用户列表
- `POST /api/admin/users` - 创建用户
- `DELETE /api/admin/users/{user_id}` - 删除用户
- `GET /api/admin/products` - 获取产品列表
- `POST /api/admin/products/from-url` - 从URL创建产品

### 产品端点
- `GET /api/products` - 获取产品列表
- `GET /api/products/categories` - 获取产品分类
- `GET /api/products/merchants` - 获取商家列表

## 重要的修复记录

### 已解决的问题
1. **JWT认证问题** - Token使用username代替user_id
2. **SQLAlchemy会话绑定错误** - 修复跨会话对象访问
3. **CORS配置** - 支持前端端口3003
4. **API路径配置** - 前端直连后端8002端口
5. **枚举序列化问题** - 用户创建时枚举转字符串

### 数据库迁移
- 添加了 `is_active` 字段到用户表
- 支持项目类型分类
- 产品图片上传和存储

## 开发注意事项

### 前端开发
- 使用Vue 3 Composition API
- 所有API调用直接连接 http://localhost:8002
- 支持中英双语切换
- Element Plus组件库统一UI风格

### 后端开发
- 使用FastAPI异步框架
- SQLAlchemy ORM管理数据库
- JWT认证保护管理员端点
- Agent模式处理AI功能

### 代码规范
- TypeScript严格类型检查
- Python类型提示
- 组件化开发
- 国际化支持

## 部署说明

### 本地开发
1. 克隆项目
2. 安装后端依赖并启动
3. 安装前端依赖并启动
4. 访问前端URL进行开发

### 数据备份
数据库文件位置：
- `backend/diy_assistant.db`
- `backend/diy_system.db`

**重要:** 这两个数据库文件包含所有用户数据、产品信息和项目记录，必须定期备份。

## 故障排除

### 常见问题
1. **端口冲突** - 前端会自动选择可用端口
2. **CORS错误** - 检查后端允许的源列表
3. **数据库连接** - 确保数据库文件存在且可写
4. **依赖缺失** - 重新安装package.json和requirements.txt

### 日志位置
- 后端日志：控制台输出
- 前端日志：浏览器控制台
- 数据库：SQLite文件直接访问

---

**最后更新:** 2025-08-17
**版本:** 1.0.0
**维护者:** Claude Code Assistant