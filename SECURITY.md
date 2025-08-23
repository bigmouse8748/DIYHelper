# 安全指南

## 🚨 密码安全问题已修复

本项目之前存在硬编码密码的安全漏洞，现已全部修复。

## 修复内容

### 1. 迁移脚本 (`DIY-Smart-Assistant-V2/scripts/migrate-data.py`)
- ✅ 移除硬编码数据库密码
- ✅ 使用环境变量 `DB_PASSWORD`
- ✅ 添加环境变量验证

### 2. ECS任务定义 (`task-def-simple.json`)
- ✅ 移除硬编码密码
- ✅ 使用AWS Secrets Manager获取 `DB_PASSWORD`
- ✅ 移除 `DATABASE_URL` 中的硬编码密码

### 3. 应用配置 (`backend/app/config.py`)
- ✅ 支持从单独环境变量构建数据库连接
- ✅ 优先使用环境变量而非硬编码值

## 安全的密码管理

### 生产环境
```bash
# 密码存储在AWS Secrets Manager中
# ECS任务会自动从Secrets Manager获取密码
```

### 开发环境
```bash
# 设置环境变量
export DB_PASSWORD="your_password_here"

# 或在运行时指定
DB_PASSWORD="your_password" python migrate-data.py
```

### 迁移脚本使用方式
```bash
# 正确的方式
DB_PASSWORD="actual_password" python DIY-Smart-Assistant-V2/scripts/migrate-data.py

# 错误的方式（会拒绝执行）
python DIY-Smart-Assistant-V2/scripts/migrate-data.py  # 没有DB_PASSWORD环境变量
```

## AWS Secrets Manager配置

密码现在存储在：
```
arn:aws:secretsmanager:us-east-1:571600828655:secret:cheasydiy-production-secrets
```

需要包含的键：
- `OPENAI_API_KEY`: OpenAI API密钥
- `JWT_SECRET_KEY`: JWT签名密钥  
- `DB_PASSWORD`: 数据库密码

## 预防措施

### Git Pre-commit Hook（推荐）
考虑添加pre-commit hook来防止提交敏感信息：

```bash
#!/bin/sh
# .git/hooks/pre-commit
if git diff --cached --name-only | xargs grep -l "ChEasyDiy2024\|password.*:" 2>/dev/null; then
    echo "❌ 检测到可能的硬编码密码！"
    echo "请使用环境变量替代硬编码密码"
    exit 1
fi
```

### .gitignore规则
```
# 敏感配置文件
.env
.env.local
.env.production
config/secrets.json
**/secrets/**
```

## 密码轮换建议

考虑到之前的密码暴露，建议：

1. **立即轮换数据库密码**
2. **更新AWS Secrets Manager中的密码**
3. **重新部署所有服务**
4. **审计访问日志**

## 报告安全问题

如发现安全问题，请：
1. 不要在公开issue中报告
2. 发送邮件到管理员
3. 提供详细的漏洞描述

## 检查清单

- ✅ 所有硬编码密码已移除
- ✅ 使用AWS Secrets Manager存储敏感信息  
- ✅ 环境变量验证已添加
- ✅ 配置文件支持安全的密码管理
- ⚠️  考虑轮换数据库密码
- ⚠️  添加pre-commit hook防止未来问题