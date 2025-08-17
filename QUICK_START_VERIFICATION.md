# 快速启动和验证指南

## 克隆项目后的验证步骤

### 1. 克隆项目
```bash
git clone [your-repository-url]
cd DIYList
git checkout local-test
```

### 2. 验证文件完整性
确认以下关键文件存在：
- ✅ `PROJECT_OVERVIEW.md` - 项目技术文档
- ✅ `DATABASE_BACKUP_GUIDE.md` - 数据库指南  
- ✅ `CLAUDE.md` - Claude开发指南
- ✅ `diy-agent-system/backend/diy_assistant.db` (36KB)
- ✅ `diy-agent-system/backend/diy_system.db` (28KB)

### 3. 启动后端
```bash
cd diy-agent-system/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main_enhanced.py
```

**预期输出:**
```
INFO:     Uvicorn running on http://0.0.0.0:8002
INFO:     Database initialized successfully
```

### 4. 启动前端
```bash
cd diy-agent-system/frontend
npm install
npm run dev
```

**预期输出:**
```
VITE ready in XXXms
Local:   http://localhost:3003/
```

### 5. 验证系统功能

#### 5.1 管理员登录测试
1. 访问: http://localhost:3003/login
2. 登录凭据: `admin` / `admin123`
3. 应该能成功登录并看到管理界面

#### 5.2 用户管理测试
1. 访问: http://localhost:3003/admin/users
2. 应该能看到用户列表（包括admin用户）
3. 测试创建用户功能

#### 5.3 产品管理测试
1. 访问: http://localhost:3003/admin/products  
2. 测试URL产品提取功能
3. 尝试用Amazon产品URL测试AI提取

#### 5.4 项目分析测试
1. 访问: http://localhost:3003/assistant
2. 上传一张DIY项目图片
3. 检查是否返回分析结果

### 6. API健康检查
```bash
# 测试后端健康状态
curl http://localhost:8002/api/test

# 测试Agent状态
curl http://localhost:8002/agents/status
```

### 7. 常见问题解决

#### 问题: 端口冲突
- 前端会自动选择端口3000-3003中的可用端口
- 后端固定使用8002端口

#### 问题: 数据库权限错误
```bash
chmod 644 diy-agent-system/backend/*.db
```

#### 问题: npm安装失败
```bash
cd diy-agent-system/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 问题: Python依赖错误
```bash
cd diy-agent-system/backend
pip install --upgrade pip
pip install -r requirements.txt
```

### 8. 确认数据保持完整

验证管理员账户存在:
- 用户名: admin
- 密码: admin123
- 权限: 管理员

验证数据库包含:
- 用户账户信息
- 产品数据（如果之前添加过）
- 系统配置信息

## 成功指标

✅ 后端正常启动在8002端口  
✅ 前端正常启动在3003端口  
✅ admin/admin123可以正常登录  
✅ 用户管理界面显示用户列表  
✅ 产品管理界面可以从URL提取产品信息  
✅ DIY分析功能可以处理图片上传  
✅ 所有API调用返回正常状态  

## 下次开发准备

1. 阅读 `PROJECT_OVERVIEW.md` 了解系统架构
2. 查看 `DATABASE_BACKUP_GUIDE.md` 了解数据管理
3. 参考 `CLAUDE.md` 获取开发指导

系统现在已经完全可用，包含完整的数据和所有功能！

---
**验证时间:** 2025-08-17  
**系统状态:** ✅ 全功能运行  
**数据完整性:** ✅ 已保存  
**文档完整性:** ✅ 已创建