# DIY Smart Assistant - Version 2

智能DIY助手平台 - 全新架构实现

## 🎯 项目特点

- **现代化架构**: Vue 3 + FastAPI + PostgreSQL
- **JWT认证**: 简化的本地认证系统
- **AI驱动**: OpenAI GPT-4 Vision API集成
- **多级权限**: free, pro, premium, admin用户类型
- **中英双语**: 完整的国际化支持

## 🏗️ 技术栈

### 前端
- Vue 3 + TypeScript + Composition API
- Element Plus UI框架
- Pinia状态管理
- Vite构建工具
- Vue I18n国际化

### 后端
- FastAPI + Python 3.11+
- SQLAlchemy ORM + PostgreSQL
- JWT认证系统
- bcrypt密码加密
- OpenAI API集成

## 🚀 快速开始

### 后端启动
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements/dev.txt
python -m app.main
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 📖 文档

详细的项目设计和实施文档请参考: [DIY_SMART_ASSISTANT_PROJECT_PLAN.md](../DIY_SMART_ASSISTANT_PROJECT_PLAN.md)

## 🔄 从旧版本迁移

这是全新的架构实现，通过脚本可以迁移现有的产品数据和用户信息。

---

**注意**: 这是重新设计的版本，采用了统一的架构和简化的认证系统，解决了旧版本中的复杂性和维护问题。