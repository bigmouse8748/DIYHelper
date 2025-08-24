# 统一开发部署策略

## 🎯 核心理念
**一套代码，多环境运行** - 通过环境变量驱动配置，消除local-aws切换的复杂性

## 📁 环境配置文件结构
```
DIY-Smart-Assistant-V2/
├── .env.development     # 本地开发环境
├── .env.production      # AWS生产环境模板
├── backend/
│   ├── app/config.py    # 统一配置管理（环境变量驱动）
│   └── .env.local       # 本地后端配置
└── frontend/
    ├── .env.development # 本地前端配置
    ├── .env.production  # 生产前端配置
    └── vite.config.ts   # 环境感知构建配置
```

## 🔧 前端统一配置方案

### api.ts 恢复环境变量驱动
```typescript
// src/utils/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### 环境配置文件
```bash
# .env.development (本地开发)
VITE_API_URL=http://localhost:8000
VITE_ENV=development

# .env.production (AWS部署)
VITE_API_URL=https://api.cheasydiy.com
VITE_ENV=production
```

## 🔧 后端统一配置方案

### config.py 环境感知配置
```python
class Settings(BaseSettings):
    # 环境标识
    environment: str = "development"
    
    # 数据库配置 - 环境自动切换
    database_url: str = ""
    
    # API配置
    cors_origins: List[str] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_environment_specific_config()
    
    def _setup_environment_specific_config(self):
        if self.environment == "production":
            # AWS生产环境配置
            self._setup_aws_config()
        else:
            # 本地开发环境配置
            self._setup_local_config()
```

## 🚀 开发流程

### 本地开发
```bash
# 1. 切换到本地分支
git checkout local-v2

# 2. 自动使用本地配置
# Frontend: .env.development
# Backend: .env.local

# 3. 正常开发
npm run dev        # 前端
python main.py     # 后端
```

### AWS部署
```bash
# 1. 合并到部署分支
git checkout aws-deployment
git merge local-v2

# 2. 自动使用生产配置
# Frontend: 构建时使用 .env.production
# Backend: 运行时读取 AWS Secrets Manager

# 3. 推送部署
git push origin aws-deployment
```

## 📋 配置映射表

| 配置项 | 本地开发 | AWS生产 |
|--------|----------|---------|
| 前端API URL | `http://localhost:8000` | `https://api.cheasydiy.com` |
| 数据库 | SQLite | PostgreSQL (RDS) |
| 密钥管理 | .env文件 | AWS Secrets Manager |
| CORS域名 | localhost:* | cheasydiy.com |
| 环境标识 | `development` | `production` |

## 🔄 分支管理策略

### 分支用途
- **local-v2**: 本地开发主分支
- **aws-deployment**: AWS部署专用分支（从local-v2自动同步）

### 工作流程
1. **功能开发**: 在 local-v2 分支开发和测试
2. **合并同步**: 定期将 local-v2 合并到 aws-deployment
3. **环境切换**: 通过环境变量自动适配，无需手动修改代码
4. **部署验证**: AWS部署后验证功能正常

## 🛡️ 安全考虑
- 生产环境密钥通过AWS Secrets Manager管理
- 开发环境使用本地.env文件（加入.gitignore）
- API密钥等敏感信息不提交到版本控制

## 🎯 优势
1. **开发效率**: 消除环境切换时的手动配置
2. **一致性**: 相同代码在不同环境运行
3. **安全性**: 生产密钥与开发环境隔离
4. **可维护性**: 配置集中管理，易于修改
5. **自动化**: 部署流程标准化，减少人工错误

## 📝 实施步骤
1. 修复前端api.ts恢复环境变量驱动
2. 更新后端config.py支持环境自动切换
3. 创建标准环境配置文件
4. 更新GitHub Actions使用环境感知构建
5. 编写详细的开发和部署文档