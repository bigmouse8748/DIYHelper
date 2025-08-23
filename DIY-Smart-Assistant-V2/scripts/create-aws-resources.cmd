@echo off
REM AWS ECS资源创建脚本 (Windows版本)
REM 用于创建DIY Smart Assistant V2的AWS基础设施

setlocal enabledelayedexpansion

REM 配置变量
set REGION=us-east-1
set CLUSTER_NAME=cheasydiy-production-cluster
set SERVICE_BACKEND=cheasydiy-production-backend
set SERVICE_FRONTEND=cheasydiy-production-frontend
set ECR_REPO_BACKEND=cheasydiy/backend
set ECR_REPO_FRONTEND=cheasydiy/frontend

echo 🚀 开始创建AWS ECS资源...

REM 1. 创建ECS集群
echo 📦 创建ECS集群: %CLUSTER_NAME%
aws ecs create-cluster --cluster-name %CLUSTER_NAME% --region %REGION% 2>nul || echo 集群可能已存在

REM 2. 创建ECR仓库
echo 📦 创建ECR仓库...
aws ecr create-repository --repository-name %ECR_REPO_BACKEND% --region %REGION% 2>nul || echo Backend仓库可能已存在
aws ecr create-repository --repository-name %ECR_REPO_FRONTEND% --region %REGION% 2>nul || echo Frontend仓库可能已存在

REM 3. 创建CloudWatch日志组
echo 📊 创建CloudWatch日志组...
aws logs create-log-group --log-group-name "/ecs/cheasydiy-backend" --region %REGION% 2>nul || echo Backend日志组可能已存在
aws logs create-log-group --log-group-name "/ecs/cheasydiy-frontend" --region %REGION% 2>nul || echo Frontend日志组可能已存在

echo ✅ 基础资源创建完成!
echo.
echo 📋 接下来需要手动创建:
echo 1. ECS任务定义 (Task Definition)
echo 2. ECS服务 (Services)
echo 3. ALB负载均衡器 (如果需要)
echo 4. 安全组配置
echo 5. VPC和子网配置
echo.
echo 💡 请参考 AWS_DEPLOYMENT_CHECKLIST.md 获取详细步骤

REM 4. 显示当前AWS账户ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo 🆔 当前AWS账户ID: %ACCOUNT_ID%
echo 🔗 ECR登录命令:
echo aws ecr get-login-password --region %REGION% ^| docker login --username AWS --password-stdin %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

pause