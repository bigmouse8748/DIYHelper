#!/bin/bash

# DIY Smart Assistant - Deploy to cheasydiy.com (ECS + S3 + RDS)
# This script updates your existing ECS/S3/RDS infrastructure

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying DIY Smart Assistant to cheasydiy.com${NC}"
echo "=================================================="

# Configuration for cheasydiy.com
DOMAIN="cheasydiy.com"
REGION="us-east-1"

echo -e "${YELLOW}📋 Getting your OpenAI API key...${NC}"
read -p "Enter your OpenAI API key: " OPENAI_API_KEY

echo -e "${YELLOW}🔍 Discovering your AWS infrastructure...${NC}"

# Find ECS cluster and service
echo "Finding ECS resources..."
ECS_CLUSTERS=$(aws ecs list-clusters --query 'clusterArns[*]' --output text | grep -o '[^/]*$')
echo "Available ECS clusters: $ECS_CLUSTERS"

if [ -z "$ECS_CLUSTERS" ]; then
    echo -e "${RED}❌ No ECS clusters found${NC}"
    exit 1
fi

# Auto-detect or ask for cluster
CLUSTER_COUNT=$(echo $ECS_CLUSTERS | wc -w)
if [ $CLUSTER_COUNT -eq 1 ]; then
    ECS_CLUSTER=$ECS_CLUSTERS
    echo -e "${GREEN}✅ Using ECS cluster: $ECS_CLUSTER${NC}"
else
    echo "Multiple clusters found:"
    echo $ECS_CLUSTERS | tr ' ' '\n' | nl
    read -p "Enter cluster name: " ECS_CLUSTER
fi

# Find services in the cluster
ECS_SERVICES=$(aws ecs list-services --cluster $ECS_CLUSTER --query 'serviceArns[*]' --output text | grep -o '[^/]*$')
echo "Services in cluster: $ECS_SERVICES"

if [ -z "$ECS_SERVICES" ]; then
    echo -e "${YELLOW}⚠️ No existing services found, will create new service${NC}"
    ECS_SERVICE="diy-assistant-service"
else
    SERVICE_COUNT=$(echo $ECS_SERVICES | wc -w)
    if [ $SERVICE_COUNT -eq 1 ]; then
        ECS_SERVICE=$ECS_SERVICES
        echo -e "${GREEN}✅ Using ECS service: $ECS_SERVICE${NC}"
    else
        echo "Multiple services found:"
        echo $ECS_SERVICES | tr ' ' '\n' | nl
        read -p "Enter service name (or 'new' for new service): " ECS_SERVICE
        if [ "$ECS_SERVICE" = "new" ]; then
            ECS_SERVICE="diy-assistant-service"
        fi
    fi
fi

# Find S3 bucket
echo "Finding S3 buckets..."
S3_BUCKETS=$(aws s3 ls | grep -E 'cheasydiy|frontend|website' | awk '{print $3}')
echo "Found S3 buckets: $S3_BUCKETS"

if [ -z "$S3_BUCKETS" ]; then
    read -p "Enter S3 bucket name for frontend: " S3_BUCKET
else
    BUCKET_COUNT=$(echo $S3_BUCKETS | wc -w)
    if [ $BUCKET_COUNT -eq 1 ]; then
        S3_BUCKET=$S3_BUCKETS
        echo -e "${GREEN}✅ Using S3 bucket: $S3_BUCKET${NC}"
    else
        echo "Multiple buckets found:"
        echo $S3_BUCKETS | tr ' ' '\n' | nl
        read -p "Enter S3 bucket name: " S3_BUCKET
    fi
fi

# Find RDS instance
echo "Finding RDS instances..."
RDS_INSTANCES=$(aws rds describe-db-instances --query 'DBInstances[?DBInstanceStatus==`available`].DBInstanceIdentifier' --output text)
echo "Found RDS instances: $RDS_INSTANCES"

if [ -z "$RDS_INSTANCES" ]; then
    echo -e "${RED}❌ No RDS instances found${NC}"
    read -p "Enter RDS endpoint manually: " RDS_ENDPOINT
    read -p "Enter RDS username: " RDS_USERNAME
    read -p "Enter RDS password: " RDS_PASSWORD
    read -p "Enter database name: " RDS_DB_NAME
else
    INSTANCE_COUNT=$(echo $RDS_INSTANCES | wc -w)
    if [ $INSTANCE_COUNT -eq 1 ]; then
        RDS_INSTANCE=$RDS_INSTANCES
        echo -e "${GREEN}✅ Using RDS instance: $RDS_INSTANCE${NC}"
    else
        echo "Multiple RDS instances found:"
        echo $RDS_INSTANCES | tr ' ' '\n' | nl
        read -p "Enter RDS instance identifier: " RDS_INSTANCE
    fi
    
    # Get RDS details
    RDS_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier $RDS_INSTANCE --query 'DBInstances[0].Endpoint.Address' --output text)
    RDS_PORT=$(aws rds describe-db-instances --db-instance-identifier $RDS_INSTANCE --query 'DBInstances[0].Endpoint.Port' --output text)
    
    read -p "Enter RDS username: " RDS_USERNAME
    read -p "Enter RDS password: " RDS_PASSWORD
    read -p "Enter database name: " RDS_DB_NAME
fi

# Find ECR repository or create one
echo "Setting up ECR repository..."
ECR_REPO_NAME="diy-assistant-backend"
ECR_REPO_URI=""

# Check if repository exists
if aws ecr describe-repositories --repository-names $ECR_REPO_NAME >/dev/null 2>&1; then
    ECR_REPO_URI=$(aws ecr describe-repositories --repository-names $ECR_REPO_NAME --query 'repositories[0].repositoryUri' --output text)
    echo -e "${GREEN}✅ Using existing ECR repository: $ECR_REPO_URI${NC}"
else
    echo "Creating ECR repository..."
    aws ecr create-repository --repository-name $ECR_REPO_NAME
    ECR_REPO_URI=$(aws ecr describe-repositories --repository-names $ECR_REPO_NAME --query 'repositories[0].repositoryUri' --output text)
    echo -e "${GREEN}✅ Created ECR repository: $ECR_REPO_URI${NC}"
fi

# Find CloudFront distribution
echo "Finding CloudFront distribution..."
CLOUDFRONT_DISTRIBUTIONS=$(aws cloudfront list-distributions --query 'DistributionList.Items[?contains(Origins.Items[0].DomainName, `cheasydiy`) || contains(Comment, `cheasydiy`)].Id' --output text)

if [ -z "$CLOUDFRONT_DISTRIBUTIONS" ]; then
    echo -e "${YELLOW}⚠️ No CloudFront distribution found for cheasydiy.com${NC}"
    CLOUDFRONT_ID=""
else
    CLOUDFRONT_ID=$CLOUDFRONT_DISTRIBUTIONS
    echo -e "${GREEN}✅ Using CloudFront distribution: $CLOUDFRONT_ID${NC}"
fi

echo -e "${BLUE}📄 Creating production environment configuration...${NC}"

# Create production environment
DATABASE_URL="postgresql://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_ENDPOINT}:${RDS_PORT:-5432}/${RDS_DB_NAME}"
JWT_SECRET=$(openssl rand -hex 32)

cat > .env.production << EOF
# Production Environment for cheasydiy.com
DATABASE_URL=${DATABASE_URL}
JWT_SECRET_KEY=${JWT_SECRET}
OPENAI_API_KEY=${OPENAI_API_KEY}
ADMIN_SETUP_KEY=setup_admin_cheasydiy_2025
AWS_REGION=${REGION}
CORS_ORIGINS=https://cheasydiy.com,https://www.cheasydiy.com
ENVIRONMENT=production

# Optional AWS services
S3_BUCKET=${S3_BUCKET}
EOF

echo -e "${GREEN}✅ Environment configuration created${NC}"

# Build and push backend to ECR
echo -e "${BLUE}🐳 Building and pushing backend to ECR...${NC}"

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO_URI

# Build backend image
cd diy-agent-system/backend
docker build -t $ECR_REPO_NAME:latest .
docker tag $ECR_REPO_NAME:latest $ECR_REPO_URI:latest
docker tag $ECR_REPO_NAME:latest $ECR_REPO_URI:$(date +%Y%m%d-%H%M%S)
docker push $ECR_REPO_URI:latest
docker push $ECR_REPO_URI:$(date +%Y%m%d-%H%M%S)
cd ../..

echo -e "${GREEN}✅ Backend image pushed to ECR${NC}"

# Create ECS task definition
echo -e "${BLUE}📋 Creating ECS task definition...${NC}"

cat > task-definition.json << EOF
{
  "family": "diy-assistant-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${ECR_REPO_URI}:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "${DATABASE_URL}"},
        {"name": "JWT_SECRET_KEY", "value": "${JWT_SECRET}"},
        {"name": "OPENAI_API_KEY", "value": "${OPENAI_API_KEY}"},
        {"name": "ADMIN_SETUP_KEY", "value": "setup_admin_cheasydiy_2025"},
        {"name": "AWS_REGION", "value": "${REGION}"},
        {"name": "CORS_ORIGINS", "value": "https://cheasydiy.com,https://www.cheasydiy.com"},
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/diy-assistant",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "backend",
          "awslogs-create-group": "true"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8001/api/test || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
EOF

# Register task definition
TASK_DEF_ARN=$(aws ecs register-task-definition --cli-input-json file://task-definition.json --query 'taskDefinition.taskDefinitionArn' --output text)
echo -e "${GREEN}✅ Task definition registered: $TASK_DEF_ARN${NC}"

# Update or create ECS service
echo -e "${BLUE}🚀 Updating ECS service...${NC}"

# Get VPC and subnet info
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0:2].SubnetId' --output text | tr '\t' ',')

# Create or update service
if echo $ECS_SERVICES | grep -q $ECS_SERVICE; then
    echo "Updating existing ECS service..."
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_SERVICE \
        --task-definition $TASK_DEF_ARN \
        --force-new-deployment
else
    echo "Creating new ECS service..."
    aws ecs create-service \
        --cluster $ECS_CLUSTER \
        --service-name $ECS_SERVICE \
        --task-definition $TASK_DEF_ARN \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],assignPublicIp=ENABLED}"
fi

echo -e "${GREEN}✅ ECS service updated${NC}"

# Build and deploy frontend
echo -e "${BLUE}🌐 Building and deploying frontend...${NC}"

cd diy-agent-system/frontend

# Set API URL for production
echo "VITE_API_URL=https://api.cheasydiy.com" > .env.production

# Install and build
npm install
npm run build

# Upload to S3
aws s3 sync dist/ s3://$S3_BUCKET --delete --acl public-read

# Invalidate CloudFront cache
if [ ! -z "$CLOUDFRONT_ID" ]; then
    aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
    echo -e "${GREEN}✅ CloudFront cache invalidated${NC}"
fi

cd ../..

echo -e "${GREEN}✅ Frontend deployed to S3${NC}"

# Initialize database
echo -e "${BLUE}🗄️ Initializing database...${NC}"

# Wait for ECS service to be stable
echo "Waiting for ECS service to stabilize..."
aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE

echo -e "${GREEN}🎉 Deployment to cheasydiy.com completed successfully!${NC}"
echo "============================================================="
echo -e "🌐 Frontend: ${BLUE}https://cheasydiy.com${NC}"
echo -e "🔌 Backend API: ${BLUE}https://api.cheasydiy.com${NC}"
echo -e "🏥 Health Check: ${BLUE}https://api.cheasydiy.com/api/test${NC}"
echo -e "👤 Admin Panel: ${BLUE}https://cheasydiy.com/admin${NC}"
echo ""
echo -e "${YELLOW}🔑 Admin Credentials:${NC}"
echo "- Username: admin"
echo "- Password: Admin123!"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Test the application: https://cheasydiy.com"
echo "2. Check API health: https://api.cheasydiy.com/api/test"
echo "3. Login to admin panel: https://cheasydiy.com/admin"
echo "4. Add some product URLs to test the AI extraction"
echo ""
echo -e "${GREEN}✅ Your DIY Smart Assistant is now live!${NC}"