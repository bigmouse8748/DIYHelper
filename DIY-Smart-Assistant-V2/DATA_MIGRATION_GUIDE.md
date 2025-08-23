# 📊 数据迁移指南

## 🎯 迁移类型说明

当前AWS部署只包含**Schema迁移**，**不包含数据迁移**：

| 迁移类型 | 状态 | 说明 |
|---------|------|------|
| **Schema迁移** | ✅ **自动执行** | 表结构、字段、索引、约束 |
| **数据迁移** | ❌ **需手动执行** | 用户数据、产品记录、历史数据 |

## 🗄️ 当前数据库状态

**RDS PostgreSQL** (生产环境):
- ✅ **表结构**: 已创建完整的表结构
- ❌ **数据记录**: 空表，无任何数据
- 🔗 **连接**: cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com:5432

**本地SQLite** (开发环境):
- 📊 **包含数据**: 用户账户、产品信息、测试数据
- 🔗 **位置**: `backend/instance/app.db`

## 🚀 数据迁移方案

### 方案1: Python脚本迁移 (推荐)

**使用场景**: 小到中等数据量 (< 10万条记录)

```bash
# 1. 安装依赖
pip install asyncpg aiosqlite

# 2. 配置数据库连接信息
# 编辑 scripts/migrate-data.py 中的连接参数

# 3. 执行迁移
cd DIY-Smart-Assistant-V2
python scripts/migrate-data.py
```

**优势**:
- ✅ 简单易用，一键执行
- ✅ 支持冲突处理 (ON CONFLICT DO NOTHING)
- ✅ 按外键依赖顺序迁移
- ✅ 详细的进度报告

### 方案2: 数据库导出/导入

**使用场景**: 大数据量或复杂数据结构

```bash
# 1. 从SQLite导出数据
sqlite3 backend/instance/app.db ".dump" > data_export.sql

# 2. 转换为PostgreSQL格式 (需要手动调整语法)
# - SQLite的 INTEGER PRIMARY KEY -> PostgreSQL的 SERIAL
# - SQLite的 TEXT -> PostgreSQL的 TEXT/VARCHAR
# - 时间格式转换

# 3. 导入到PostgreSQL
psql -h cheasydiy-production-db.c9sieeomsxup.us-east-1.rds.amazonaws.com \
     -U dbadmin -d cheasydiy < data_export.sql
```

### 方案3: ECS任务迁移 (生产级)

**使用场景**: 大数据量，需要在AWS内部执行

```yaml
# GitHub Actions中添加数据迁移任务
- name: Run Data Migration
  run: |
    # 运行专门的迁移容器任务
    aws ecs run-task \
      --cluster cheasydiy-production-cluster \
      --task-definition migration-task \
      --overrides '{
        "containerOverrides": [{
          "name": "migrator",
          "command": ["python", "scripts/migrate-data.py"]
        }]
      }'
```

## ⚠️ 重要注意事项

### 🔒 数据安全
- **备份优先**: 迁移前备份本地数据
- **测试环境**: 先在测试环境验证
- **敏感数据**: 检查密码、API密钥等敏感信息

### 🔄 数据一致性
- **外键顺序**: 按依赖关系迁移 (users → products → others)
- **数据类型**: 确保SQLite和PostgreSQL类型兼容
- **约束检查**: 验证唯一约束、非空约束

### 📊 迁移验证
```sql
-- 检查记录数量
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL  
SELECT 'product_analyses', COUNT(*) FROM product_analyses;

-- 检查数据完整性
SELECT COUNT(*) FROM products WHERE title IS NULL; -- 应该为0
SELECT COUNT(*) FROM users WHERE email IS NULL; -- 应该为0
```

## 🎯 推荐执行顺序

1. **✅ 完成当前Schema迁移** (正在进行)
2. **🔍 验证表结构正确**
3. **📊 评估数据量大小**
4. **🛠️ 选择合适的迁移方案**
5. **🧪 测试环境验证**
6. **🚀 生产环境迁移**
7. **✅ 验证数据完整性**

## 📞 如果不需要数据迁移

如果您的应用可以从空数据库开始，那么当前的Schema迁移就足够了：

- ✅ **新用户注册**: 直接在RDS中创建
- ✅ **新产品录入**: 通过管理界面添加
- ✅ **历史数据**: 可选择性迁移重要数据

**这是最安全的方案，避免了数据迁移的复杂性和风险。**