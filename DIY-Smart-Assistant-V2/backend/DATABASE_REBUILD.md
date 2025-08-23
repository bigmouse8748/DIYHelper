# 数据库重建指南

## 概述

由于数据库schema版本不匹配，需要完整重建数据库以确保与当前SQLAlchemy模型一致。

## 脚本说明

### 1. `rebuild_database.py`
- **功能**: 完整重建数据库
- **操作**: 删除所有现有表，使用当前SQLAlchemy模型重新创建
- **安全**: 需要手动确认才能执行（输入 'YES'）

### 2. `test_rebuilt_database.py` 
- **功能**: 测试重建后的数据库
- **操作**: 验证表结构，测试基本CRUD操作
- **用途**: 确保重建成功

## 执行步骤

### 在AWS ECS容器中执行：

1. **连接到ECS容器**:
```bash
# 获取任务ARN
aws ecs list-tasks --cluster cheasydiy-production-cluster --service-name cheasydiy-production-backend

# 连接到容器
aws ecs execute-command \
  --cluster cheasydiy-production-cluster \
  --task <TASK_ARN> \
  --container backend \
  --interactive \
  --command "/bin/bash"
```

2. **在容器内执行重建**:
```bash
cd /app
python rebuild_database.py
# 输入 'YES' 确认
```

3. **测试数据库**:
```bash
python test_rebuilt_database.py
```

4. **重启服务** (确保应用使用新的数据库schema):
```bash
# 退出容器后在本地执行
aws ecs update-service \
  --cluster cheasydiy-production-cluster \
  --service cheasydiy-production-backend \
  --force-new-deployment
```

### 本地测试（可选）:

```bash
cd DIY-Smart-Assistant-V2/backend

# 设置环境变量（请使用实际密码）
export DB_PASSWORD="your_actual_password_here"
export DATABASE_URL="postgresql://dbadmin:${DB_PASSWORD}@cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com:5432/cheasydiy"

# 执行重建（小心！这会影响生产数据库）
python rebuild_database.py

# 测试
python test_rebuilt_database.py
```

## 新的数据库schema

重建后的users表将包含以下列：
- `id`: 主键
- `username`: 用户名（唯一）
- `email`: 邮箱（唯一）
- `password_hash`: 密码哈希
- `full_name`: 全名
- `avatar_url`: 头像URL
- `user_type`: 用户类型（free/pro/premium/admin）
- `is_active`: 是否活跃
- `email_verified`: 邮箱是否验证
- `email_verify_token`: 邮箱验证令牌
- `password_reset_token`: 密码重置令牌
- `password_reset_expires`: 密码重置过期时间
- `failed_login_attempts`: 失败登录次数
- `locked_until`: 锁定到什么时候
- `last_login`: 最后登录时间
- `phone`: 电话号码
- `location`: 位置
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 注意事项

⚠️ **重要警告**:
- 此操作会删除所有现有数据
- 在生产环境中执行前请确保已备份重要数据
- 执行后需要重新注册所有用户

🔧 **维护相关**:
- 删除了main.py中的自动schema迁移代码
- 未来的schema更新应使用专门的迁移脚本
- 所有模型变更都应反映在SQLAlchemy模型中

## 回滚方案

如果重建失败，可以：
1. 使用之前的数据库备份恢复
2. 重新部署之前的应用版本
3. 检查CloudWatch日志排查问题

## 验证成功

重建成功的标志：
1. `rebuild_database.py` 输出 "🎉 数据库重建完成!"
2. `test_rebuilt_database.py` 输出 "🎉 数据库测试完成!"
3. 前端注册功能正常工作
4. CloudWatch日志中不再有数据库列错误