#!/bin/bash

# AWS ECS资源创建脚本
# 用于创建DIY Smart Assistant V2的AWS基础设施

set -e

# 配置变量
REGION="us-east-1"
CLUSTER_NAME="cheasydiy-production-cluster"
SERVICE_BACKEND="cheasydiy-production-backend"
SERVICE_FRONTEND="cheasydiy-production-frontend"
ECR_REPO_BACKEND="cheasydiy/backend"
ECR_REPO_FRONTEND="cheasydiy/frontend"

echo "🚀 开始创建AWS ECS资源..."

# 1. 创建ECS集群
echo "📦 创建ECS集群: $CLUSTER_NAME"
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION || echo "集群可能已存在"

# 2. 创建ECR仓库
echo "📦 创建ECR仓库..."
aws ecr create-repository --repository-name $ECR_REPO_BACKEND --region $REGION || echo "Backend仓库可能已存在"
aws ecr create-repository --repository-name $ECR_REPO_FRONTEND --region $REGION || echo "Frontend仓库可能已存在"

# 3. 创建CloudWatch日志组
echo "📊 创建CloudWatch日志组..."
aws logs create-log-group --log-group-name "/ecs/cheasydiy-backend" --region $REGION || echo "Backend日志组可能已存在"
aws logs create-log-group --log-group-name "/ecs/cheasydiy-frontend" --region $REGION || echo "Frontend日志组可能已存在"

echo "✅ 基础资源创建完成!"
echo ""
echo "📋 接下来需要手动创建:"
echo "1. ECS任务定义 (Task Definition)"
echo "2. ECS服务 (Services)" 
echo "3. ALB负载均衡器 (如果需要)"
echo "4. 安全组配置"
echo "5. VPC和子网配置"
echo ""
echo "💡 请参考 AWS_DEPLOYMENT_CHECKLIST.md 获取详细步骤"

# 4. 显示当前AWS账户ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "🆔 当前AWS账户ID: $ACCOUNT_ID"
echo "🔗 ECR登录命令:"
echo "aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"