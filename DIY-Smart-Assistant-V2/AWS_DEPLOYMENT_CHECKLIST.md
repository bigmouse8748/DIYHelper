# 🚀 AWS部署检查清单 - DIY Smart Assistant V2

## 📋 部署前准备

### 1. GitHub Secrets配置 (必须)

请在GitHub仓库设置中配置以下Secrets:

**进入路径**: GitHub仓库 → Settings → Secrets and variables → Actions

| Secret名称 | 值说明 | 示例 |
|-----------|--------|------|
| `AWS_ACCESS_KEY_ID` | AWS访问密钥ID | AKIAIOSFODNN7EXAMPLE |
| `AWS_SECRET_ACCESS_KEY` | AWS访问密钥 | wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY |
| `AWS_ACCOUNT_ID` | AWS账户ID | 123456789012 |
| `OPENAI_API_KEY` | OpenAI API密钥 | sk-proj-xxxxx (您提供的密钥) |
| `VITE_API_URL` | 生产API地址 | https://api.cheasydiy.com |
| `S3_BUCKET_NAME` | S3存储桶名称 | cheasydiy.com |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront分发ID | E1234567890ABC |

### 2. AWS资源确认

确保以下AWS资源已存在:

- [ ] ECS集群: `cheasydiy-production-cluster`
- [ ] ECR仓库: `cheasydiy/backend`, `cheasydiy/frontend`
- [ ] ALB: 指向api.cheasydiy.com
- [ ] CloudFront: 配置cheasydiy.com
- [ ] Route53: DNS记录配置正确

### 3. 数据库配置 (如果使用RDS)

在ECS任务定义中设置:
```json
{
  "name": "DATABASE_URL",
  "value": "postgresql://username:password@rds-endpoint:5432/dbname"
}
```

## 🔄 部署步骤

### 步骤1: 合并最新代码
```bash
git checkout aws-deployment
git merge local-v2
```
✅ 已完成

### 步骤2: 推送触发部署
```bash
git push origin aws-deployment
```

### 步骤3: 监控部署过程

1. **查看GitHub Actions**:
   - 访问: https://github.com/bigmouse8748/DIYHelper/actions
   - 查看部署进度

2. **AWS控制台监控**:
   - ECS: 查看任务运行状态
   - CloudWatch: 查看日志
   - ALB: 检查目标健康状况

### 步骤4: 验证部署
```bash
# Windows
scripts\verify-deployment.cmd

# Linux/Mac
bash scripts/verify-deployment.sh
```

## ⚠️ 重要提醒

### OpenAI API密钥
您提供的密钥需要在以下位置配置:

1. **GitHub Secrets**: `OPENAI_API_KEY`
2. **AWS Secrets Manager** (生产环境):
```bash
aws secretsmanager create-secret \
  --name diy-assistant/openai-api-key \
  --secret-string "sk-proj-mjb6bApgguvABRqIG1IuBtIu5PerDvFltrSA..."
```

### 环境变量映射

| 本地开发 | AWS生产 |
|---------|---------|
| SQLite数据库 | PostgreSQL (RDS) |
| http://localhost:8000 | https://api.cheasydiy.com |
| http://localhost:8080 | https://cheasydiy.com |
| DEBUG=true | DEBUG=false |

## 🎯 快速部署命令

一键部署到AWS:
```bash
# 在aws-deployment分支
git push origin aws-deployment
```

## 🔍 故障排查

### 如果部署失败

1. **检查GitHub Actions日志**
2. **验证AWS权限**
3. **检查环境变量配置**
4. **查看CloudWatch日志**

### 回滚方法
```bash
git revert HEAD
git push origin aws-deployment
```

## ✅ 部署成功标志

- [ ] GitHub Actions显示绿色✅
- [ ] https://api.cheasydiy.com/api/v1/health 返回200
- [ ] https://cheasydiy.com 可正常访问
- [ ] 能够上传图片并获得分析结果
- [ ] 管理界面正常工作

## 📞 支持

如遇到问题，请检查:
- GitHub Actions日志
- AWS CloudWatch日志
- ECS任务状态
- ALB目标健康检查