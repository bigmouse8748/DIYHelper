#!/bin/bash

# Quick update script for existing AWS services
# This script helps you deploy to your current infrastructure with minimal changes

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Quick Update for Existing AWS Service${NC}"
echo "=========================================="

# Quick deployment options
echo -e "${YELLOW}Choose your deployment method:${NC}"
echo "1) Update existing EC2 instance"
echo "2) Update existing ECS service" 
echo "3) Replace existing container"
echo "4) Update S3 static site only"

read -p "Select option (1-4): " DEPLOY_METHOD

case $DEPLOY_METHOD in
    1)
        # EC2 Update
        read -p "Enter EC2 instance IP: " EC2_IP
        read -p "Enter key file name (without .pem): " KEY_NAME
        read -p "Enter OpenAI API key: " OPENAI_API_KEY
        
        echo -e "${YELLOW}🚀 Updating EC2 instance...${NC}"
        
        # Create quick .env file
        cat > .env.production << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
JWT_SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./production.db
CORS_ORIGINS=http://${EC2_IP}:8001,http://${EC2_IP}
ADMIN_SETUP_KEY=setup_admin_prod_2025
ENVIRONMENT=production
EOF
        
        # Package application
        tar -czf diy-update.tar.gz \
            diy-agent-system/ \
            docker-compose.yml \
            .env.production \
            --exclude=node_modules \
            --exclude=.git
        
        # Upload and deploy
        scp -i ${KEY_NAME}.pem diy-update.tar.gz ec2-user@${EC2_IP}:/tmp/
        
        ssh -i ${KEY_NAME}.pem ec2-user@${EC2_IP} << 'ENDSSH'
cd /home/ec2-user

# Backup existing if present
if [ -d "DIYList" ]; then
    mv DIYList DIYList-backup-$(date +%Y%m%d-%H%M%S)
fi

# Extract new version
mkdir -p DIYList
cd DIYList
tar -xzf /tmp/diy-update.tar.gz
cp .env.production .env

# Stop existing containers
docker-compose down 2>/dev/null || true

# Start new containers
docker-compose up --build -d

# Show status
echo "Containers status:"
docker-compose ps

# Test API
sleep 10
curl -f http://localhost:8001/api/test && echo "✅ API is working!" || echo "❌ API test failed"
ENDSSH
        
        echo -e "${GREEN}✅ EC2 update completed!${NC}"
        echo -e "API: ${BLUE}http://${EC2_IP}:8001${NC}"
        ;;
        
    2)
        # ECS Update
        read -p "Enter ECS cluster name: " ECS_CLUSTER
        read -p "Enter ECS service name: " ECS_SERVICE
        read -p "Enter ECR repository URI: " ECR_REPO
        
        echo -e "${YELLOW}🚀 Updating ECS service...${NC}"
        
        # Build and push to ECR
        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ECR_REPO}
        
        cd diy-agent-system/backend
        docker build -t ${ECR_REPO}:latest .
        docker push ${ECR_REPO}:latest
        cd ../..
        
        # Force new deployment
        aws ecs update-service \
            --cluster ${ECS_CLUSTER} \
            --service ${ECS_SERVICE} \
            --force-new-deployment
        
        echo -e "${GREEN}✅ ECS service update initiated!${NC}"
        ;;
        
    3)
        # Docker Container Update
        read -p "Enter container name to replace: " CONTAINER_NAME
        read -p "Enter OpenAI API key: " OPENAI_API_KEY
        
        echo -e "${YELLOW}🚀 Replacing container...${NC}"
        
        # Stop existing container
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        
        # Build new image
        cd diy-agent-system/backend
        docker build -t diy-assistant-backend:latest .
        cd ../..
        
        # Run new container
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p 8001:8001 \
            -e OPENAI_API_KEY=${OPENAI_API_KEY} \
            -e JWT_SECRET_KEY=$(openssl rand -hex 32) \
            -e DATABASE_URL=sqlite:///./production.db \
            -e CORS_ORIGINS="*" \
            --restart unless-stopped \
            diy-assistant-backend:latest
        
        echo -e "${GREEN}✅ Container replaced!${NC}"
        ;;
        
    4)
        # S3 Frontend Only
        read -p "Enter S3 bucket name: " S3_BUCKET
        read -p "Enter API URL (e.g., https://api.yourdomain.com): " API_URL
        read -p "CloudFront distribution ID (optional): " CLOUDFRONT_ID
        
        echo -e "${YELLOW}🌐 Updating frontend...${NC}"
        
        cd diy-agent-system/frontend
        
        # Set API URL
        echo "VITE_API_URL=${API_URL}" > .env.production
        
        # Build
        npm install
        npm run build
        
        # Upload to S3
        aws s3 sync dist/ s3://${S3_BUCKET} --delete --acl public-read
        
        # Invalidate CloudFront if provided
        if [ ! -z "$CLOUDFRONT_ID" ]; then
            aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_ID} --paths "/*"
        fi
        
        cd ../..
        echo -e "${GREEN}✅ Frontend updated!${NC}"
        echo -e "URL: ${BLUE}http://${S3_BUCKET}.s3-website-us-east-1.amazonaws.com${NC}"
        ;;
        
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Update completed!${NC}"
echo ""
echo -e "${YELLOW}📝 Testing URLs:${NC}"
case $DEPLOY_METHOD in
    1|3) echo "- API Health: http://${EC2_IP}:8001/api/test" ;;
    4) echo "- Frontend: http://${S3_BUCKET}.s3-website-us-east-1.amazonaws.com" ;;
esac

echo ""
echo -e "${YELLOW}🔑 Admin credentials:${NC}"
echo "- Username: admin"
echo "- Password: Admin123!"