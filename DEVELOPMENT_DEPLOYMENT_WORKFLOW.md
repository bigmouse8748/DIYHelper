# 🔄 统一开发部署工作流程

## 📋 概述
这个文档描述了基于环境变量驱动的统一开发部署流程，解决了local-v2和aws-deployment分支之间的切换复杂性。

## 🎯 核心原则
- **一套代码，多环境运行**
- **环境变量驱动配置**
- **自动化环境切换**
- **最小化手动配置**

## 🔧 环境配置

### 开发环境（Local）
```bash
# 前端 (.env.development)
VITE_API_URL=http://localhost:8000
VITE_ENV=development

# 后端 (.env.local)
ENVIRONMENT=development
DATABASE_URL=sqlite:///./diy_assistant.db
DEBUG=true
```

### 生产环境（AWS）
```bash
# 前端 (.env.production)  
VITE_API_URL=https://api.cheasydiy.com
VITE_ENV=production

# 后端 (AWS Secrets Manager)
ENVIRONMENT=production
DATABASE_URL=postgresql://...
DEBUG=false
```

## 🚀 开发流程

### 1. 本地开发
```bash
# 切换到本地开发分支
git checkout local-v2

# 启动后端 (自动使用 .env.local)
cd DIY-Smart-Assistant-V2/backend
python main.py

# 启动前端 (自动使用 .env.development)
cd DIY-Smart-Assistant-V2/frontend
npm run dev
```

**自动配置：**
- ✅ 前端连接到 `http://localhost:8000`
- ✅ 后端使用SQLite数据库
- ✅ CORS允许localhost域名
- ✅ Debug模式启用

### 2. 部署到AWS
```bash
# 合并到部署分支
git checkout aws-deployment
git merge local-v2

# 推送触发自动部署
git push origin aws-deployment
```

**自动配置：**
- ✅ 前端自动构建生产版本（使用 .env.production）
- ✅ 后端自动使用AWS Secrets Manager
- ✅ 数据库自动切换到PostgreSQL
- ✅ CORS自动配置生产域名

## 📁 文件结构
```
DIY-Smart-Assistant-V2/
├── frontend/
│   ├── .env.development      # 本地开发配置
│   ├── .env.production       # 生产部署配置
│   ├── .env.local           # 个人本地覆盖（不提交）
│   ├── src/utils/api.ts     # 环境变量驱动的API配置
│   └── Dockerfile           # 支持环境感知构建
├── backend/
│   ├── .env.local           # 本地开发配置  
│   ├── app/config.py        # 环境自动切换配置
│   └── app/main.py          # 使用环境感知的CORS配置
└── .github/workflows/
    └── aws-deploy.yml       # 环境感知的部署流程
```

## 🔍 环境检测机制

### 前端环境检测
```typescript
// src/utils/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### 后端环境检测  
```python
# app/config.py
class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    def _setup_environment_specific_config(self):
        if self.environment == "production":
            self._setup_production_config()  # AWS配置
        else:
            self._setup_development_config()  # 本地配置
```

## 🔄 自动切换特性

| 配置项 | 开发环境 | 生产环境 |
|--------|----------|----------|
| **前端API URL** | `localhost:8000` | `api.cheasydiy.com` |
| **数据库** | SQLite | PostgreSQL (RDS) |
| **密钥管理** | .env文件 | AWS Secrets Manager |
| **CORS域名** | localhost:* | cheasydiy.com |
| **调试模式** | 启用 | 禁用 |
| **构建模式** | 开发 | 生产优化 |

## 🛡️ 安全措施
- 生产密钥通过AWS Secrets Manager管理
- 本地配置文件 `.env.local` 加入 `.gitignore`
- 环境变量验证和默认值
- 生产环境自动禁用debug模式

## 🎯 优势
1. **开发效率** - 无需手动修改配置
2. **一致性** - 相同代码在不同环境运行
3. **安全性** - 生产密钥与开发环境隔离
4. **可维护性** - 配置集中管理
5. **自动化** - 部署流程标准化

## 🚨 重要提醒

### ✅ 正确做法
```bash
# 开发时
git checkout local-v2
# 自动使用开发配置，无需修改代码

# 部署时
git checkout aws-deployment
git merge local-v2
git push origin aws-deployment
# 自动使用生产配置，无需修改代码
```

### ❌ 避免的做法  
```bash
# 不要手动修改API URL
const API_BASE_URL = 'https://api.cheasydiy.com' // ❌ 硬编码

# 不要在代码中写死配置
allow_origins=["https://cheasydiy.com"] // ❌ 硬编码
```

## 📈 未来扩展
- 支持更多环境（staging, testing）
- 环境配置验证工具
- 自动化环境配置同步
- 配置管理界面

---

这个统一方案确保了您在local-v2和aws-deployment分支之间的无缝切换，消除了手动配置的复杂性！