# 数据库备份和恢复指南

## 数据库文件位置

本项目使用SQLite数据库，数据库文件位于：
- `diy-agent-system/backend/diy_assistant.db` - 主数据库 (36KB)
- `diy-agent-system/backend/diy_system.db` - 系统数据库 (28KB)

## 备份数据

### 自动备份（推荐）
数据库文件已经包含在git仓库中，每次提交都会自动备份。

### 手动备份
如果需要手动备份，请复制以下文件：
```bash
# 进入后端目录
cd diy-agent-system/backend

# 创建备份目录
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# 备份数据库文件
cp diy_assistant.db backups/$(date +%Y%m%d_%H%M%S)/
cp diy_system.db backups/$(date +%Y%m%d_%H%M%S)/
```

## 恢复数据

### 从Git恢复
1. 克隆项目：`git clone [repository_url]`
2. 切换到local-test分支：`git checkout local-test`
3. 数据库文件自动包含在项目中

### 从手动备份恢复
1. 将备份的`.db`文件复制到`diy-agent-system/backend/`目录
2. 确保文件名正确：
   - `diy_assistant.db`
   - `diy_system.db`
3. 重启后端服务

## 数据库内容

### diy_assistant.db 包含:
- 用户账户信息（包括管理员账户admin/admin123）
- 产品信息和推荐数据
- DIY项目分析历史
- 工具识别记录

### diy_system.db 包含:
- 系统配置信息
- 元数据和缓存
- Agent执行历史

## 重要提醒

1. **Git提交包含数据库**：这些.db文件已经包含在git仓库中，确保提交时包含这些文件
2. **管理员账户保持**：admin/admin123账户信息存储在数据库中
3. **产品数据保持**：所有通过管理界面添加的产品数据都会保存
4. **用户数据保持**：所有注册用户和权限设置都会保存

## 验证数据完整性

启动系统后，检查以下内容确认数据恢复成功：
1. 使用admin/admin123登录管理界面
2. 检查用户管理页面是否显示用户列表
3. 检查产品管理页面是否显示产品数据
4. 尝试进行一次项目分析，确认系统正常工作

## 故障排除

### 数据库文件权限问题
```bash
chmod 644 diy_assistant.db diy_system.db
```

### 数据库文件损坏
如果数据库文件损坏，可以删除文件并重新启动系统，会自动创建新的空数据库：
```bash
rm diy_assistant.db diy_system.db
python main_enhanced.py  # 会自动创建新数据库
```

### 重置管理员密码
如果忘记管理员密码，可以运行重置脚本：
```bash
python reset_admin_password.py
```

---
**创建时间:** 2025-08-17
**数据库大小:** diy_assistant.db (36KB), diy_system.db (28KB)
**管理员账户:** admin/admin123