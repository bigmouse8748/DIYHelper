# AWS Deployment Branch Strategy Guide

## 分支管理策略

我们采用双分支策略来分离开发和部署：

### 🔧 local-v2 分支
- **用途**: 本地开发和功能开发
- **内容**: 
  - 完整的应用代码
  - 开发环境配置
  - 测试和调试功能
- **特点**: 
  - 不包含生产部署配置
  - 专注于功能开发
  - 本地测试环境

### 🚀 aws-deployment 分支  
- **用途**: AWS生产环境部署
- **内容**:
  - 应用代码（从local-v2同步）
  - Docker生产配置文件
  - GitHub Actions工作流
  - AWS部署脚本
- **特点**:
  - 自动触发CI/CD流程
  - 直接部署到cheasydiy.com
  - 生产环境优化

## 🔄 工作流程

### 开发阶段
```bash
# 1. 在local-v2分支进行开发
git checkout local-v2
# 进行代码开发...
git add .
git commit -m "feat: 新功能开发"
git push origin local-v2
```

### 部署阶段
```bash
# 2. 将开发完成的功能合并到aws-deployment分支
git checkout aws-deployment
git merge local-v2

# 3. 推送到aws-deployment触发自动部署
git push origin aws-deployment
# 🚀 GitHub Actions自动部署到AWS
```

## 📋 部署配置

### GitHub Actions触发条件
- **触发分支**: `aws-deployment`
- **触发事件**: push, pull_request, workflow_dispatch
- **部署条件**: 只在aws-deployment分支执行

### Docker配置
- **后端**: `DIY-Smart-Assistant-V2/backend/Dockerfile`
  - 基于Python 3.11-slim
  - 生产环境优化
  - 健康检查配置
  
- **前端**: `DIY-Smart-Assistant-V2/frontend/Dockerfile`
  - 多阶段构建
  - Nginx生产配置
  - 缓存优化

### AWS服务配置
- **ECS集群**: cheasydiy-production-cluster
- **ECR仓库**: cheasydiy/backend, cheasydiy/frontend
- **域名**: https://cheasydiy.com, https://api.cheasydiy.com
- **CDN**: CloudFront + S3

## 🚨 重要注意事项

### 1. 分支同步
- 定期将local-v2的更新合并到aws-deployment
- 保持两个分支的代码一致性

### 2. 配置管理
- 部署配置只存在于aws-deployment分支
- 开发配置只存在于local-v2分支

### 3. 测试流程
```bash
# 部署前验证
git checkout aws-deployment
git merge local-v2
# 检查差异
git diff HEAD~1
# 确认无误后推送
git push origin aws-deployment
```

## 📊 监控和验证

### 部署状态检查
```bash
# 运行部署验证脚本
scripts/verify-deployment.cmd  # Windows
bash scripts/verify-deployment.sh  # Linux/Mac
```

### AWS控制台监控
- ECS服务状态
- CloudWatch日志
- CloudFront分发状态
- ALB目标健康状况

## 🔧 故障排除

### 部署失败时
1. 检查GitHub Actions日志
2. 验证AWS权限和配置
3. 回滚到前一个稳定版本：
   ```bash
   git revert HEAD
   git push origin aws-deployment
   ```

### 代码同步问题
```bash
# 重置aws-deployment分支到local-v2状态
git checkout aws-deployment
git reset --hard local-v2
git push origin aws-deployment --force-with-lease
```

## 📝 快速部署指令

```bash
# 一键从开发到部署
git checkout local-v2
# 完成开发工作...
git add . && git commit -m "完成功能开发"
git push origin local-v2

git checkout aws-deployment
git merge local-v2
git push origin aws-deployment
# 🚀 自动部署开始
```

## 🎯 优势

✅ **清晰分离**: 开发和部署配置完全分离
✅ **安全性**: 生产配置不会影响开发环境  
✅ **灵活性**: 可以独立管理部署配置
✅ **可控性**: 明确控制何时部署到生产环境
✅ **可追溯**: 清晰的部署历史记录