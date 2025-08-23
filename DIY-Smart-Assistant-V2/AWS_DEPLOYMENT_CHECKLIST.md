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
| `S3_BUCKET_NAME` | S3存储桶名称 | cheasydiy-production-frontend |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront分发ID | E1234567890ABC |

### 2. AWS资源状态确认 ✅

**根据Terraform配置，以下AWS资源已存在并正在运行**:

#### 🏗️ 基础设施 (已部署)
- ✅ **VPC**: `cheasydiy-production-vpc` (10.0.0.0/16)
- ✅ **公共子网**: `cheasydiy-production-public-1/2` 
- ✅ **私有子网**: `cheasydiy-production-private-1/2`
- ✅ **安全组**: ALB, ECS, RDS 安全组已配置
- ✅ **NAT网关**: 用于私有子网访问外网

#### 🐳 容器服务 (已部署)
- ✅ **ECS集群**: `cheasydiy-production-cluster`
- ✅ **ECR仓库**: `cheasydiy/backend`, `cheasydiy/frontend`
- ✅ **ECS后端服务**: `cheasydiy-production-backend` (Fargate Spot优化)
- ✅ **任务定义**: backend任务已配置 (512 CPU, 1024 Memory)
- ✅ **成本优化**: 80% Fargate Spot + 20% Fargate fallback (~56% 成本节省)

#### 🌐 网络和CDN (已部署)
- ✅ **ALB**: 应用负载均衡器连接ECS后端
- ✅ **S3存储桶**: `cheasydiy-production-frontend` (前端静态文件)
- ✅ **CloudFront**: 全球CDN分发
- ✅ **Route53**: DNS记录指向cheasydiy.com
- ✅ **SSL证书**: ACM证书已配置

#### 🗄️ 数据存储 (已部署)
- ✅ **RDS PostgreSQL**: `cheasydiy-production-db`
- ✅ **Secrets Manager**: 存储API密钥和敏感信息
- ✅ **S3上传桶**: `cheasydiy-production-uploads`

#### 📊 监控和日志 (已部署)
- ✅ **CloudWatch**: 日志组 `/ecs/cheasydiy-production`
- ✅ **IAM角色**: 任务执行和应用角色已配置

#### 🗄️ 数据库Schema管理 (新增)

**数据库迁移策略**:
- ✅ **Alembic迁移系统**: 版本化数据库Schema变更
- ✅ **自动化部署**: GitHub Actions自动运行迁移
- ✅ **零停机迁移**: 使用临时ECS任务执行迁移
- ✅ **回滚支持**: 支持Schema版本回滚

**迁移执行流程**:
1. **构建新镜像**: 包含最新代码和迁移文件
2. **运行迁移任务**: 临时ECS任务执行 `alembic upgrade head`
3. **验证迁移**: 检查任务退出码确保成功
4. **部署新版本**: 迁移成功后更新ECS服务

**手动迁移命令** (如果需要):
```bash
# 生成新迁移
alembic revision --autogenerate -m "Add new fields"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

#### 💰 成本优化配置 (Fargate Spot)

**容量提供策略**:
- **80% Fargate Spot**: 低成本，最多节省70%费用
- **20% 常规Fargate**: 高可用性fallback

**优势**:
- ✅ **大幅成本降低**: 相比100%常规Fargate节省~56%
- ✅ **高可用性**: Spot实例不可用时自动切换到常规Fargate
- ✅ **零配置**: ECS自动处理实例中断和替换
- ✅ **适合生产环境**: 对于无状态应用完全安全

**注意事项**:
- ⚠️ **实例可能被中断**: AWS会提前2分钟通知
- ⚠️ **启动时间略长**: Spot实例可能需要更长时间获取
- ✅ **适用场景**: Web API、微服务、批处理任务

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

## 🎯 S3缓存控制配置（手动配置）

由于AWS CLI在GitHub Actions中的缓存控制命令语法问题，建议通过AWS控制台手动配置：

### 配置步骤：

1. **登录AWS S3控制台**
2. **进入您的bucket** (`cheasydiy-production-frontend`)
3. **配置HTML文件缓存**：
   - 选择 `index.html` 文件
   - 点击 **操作** → **编辑元数据**
   - 添加元数据：`Cache-Control: no-cache, no-store, must-revalidate`
   
4. **配置静态资源缓存**：
   - 选择 `assets/` 文件夹下的所有文件
   - 点击 **操作** → **编辑元数据**
   - 添加元数据：`Cache-Control: public, max-age=31536000`

### 缓存策略说明：

| 文件类型 | 缓存策略 | 说明 |
|---------|---------|------|
| `index.html` | `no-cache, no-store, must-revalidate` | 无缓存，确保更新立即生效 |
| `assets/*.js` | `public, max-age=31536000` | 1年长期缓存，提升性能 |
| `assets/*.css` | `public, max-age=31536000` | 1年长期缓存，提升性能 |
| `assets/*.png/jpg` | `public, max-age=31536000` | 1年长期缓存，提升性能 |

### 验证缓存配置：

```bash
# 检查HTML文件缓存头
curl -I https://cheasydiy.com/

# 检查静态资源缓存头
curl -I https://cheasydiy.com/assets/index-xxxxx.js
```

## ✅ 部署成功标志

- [ ] GitHub Actions显示绿色✅
- [ ] https://api.cheasydiy.com/api/v1/health 返回200
- [ ] https://cheasydiy.com 可正常访问
- [ ] 能够上传图片并获得分析结果
- [ ] 管理界面正常工作
- [ ] S3缓存控制配置正确

## 📞 支持

如遇到问题，请检查:
- GitHub Actions日志
- AWS CloudWatch日志
- ECS任务状态
- ALB目标健康检查