#!/bin/bash

# DIY Smart Assistant - AWS Deployment Script
# This script helps deploy your application to AWS quickly

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="diy-assistant"
REGION="us-east-1"
STACK_NAME="diy-assistant-stack"

echo -e "${BLUE}🚀 DIY Smart Assistant - AWS Deployment${NC}"
echo "========================================"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Get user input
echo -e "${YELLOW}📝 Configuration Setup${NC}"
read -p "Enter your domain name (or press Enter for AWS-generated URL): " DOMAIN_NAME
read -p "Enter your OpenAI API key: " OPENAI_API_KEY
read -p "Enter a strong JWT secret key (or press Enter to generate): " JWT_SECRET

if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT secret: $JWT_SECRET"
fi

# Create .env.production file
echo -e "${YELLOW}📄 Creating production environment file...${NC}"
cat > .env.production << EOF
# Production Environment Configuration
DATABASE_URL=postgresql://dbadmin:ChEasyDiy2024!@diy-assistant-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/cheasydiy
JWT_SECRET_KEY=${JWT_SECRET}
OPENAI_API_KEY=${OPENAI_API_KEY}
ADMIN_SETUP_KEY=setup_admin_prod_2025
AWS_REGION=${REGION}
CORS_ORIGINS=https://${DOMAIN_NAME:-*.amazonaws.com}
ENVIRONMENT=production
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Option 1: Simple EC2 Deployment
echo -e "${YELLOW}🏗️  Deployment Options:${NC}"
echo "1) Simple EC2 + S3 Deployment (Recommended for beginners)"
echo "2) Scalable ECS + RDS Deployment (Production ready)"
echo "3) Serverless Lambda Deployment (Cost optimized)"

read -p "Choose deployment option (1-3): " DEPLOY_OPTION

case $DEPLOY_OPTION in
    1)
        echo -e "${BLUE}🏗️  Starting Simple EC2 + S3 Deployment...${NC}"
        
        # Launch EC2 instance
        echo -e "${YELLOW}📦 Launching EC2 instance...${NC}"
        
        # Create security group
        aws ec2 create-security-group \
            --group-name ${APP_NAME}-sg \
            --description "Security group for DIY Assistant" \
            --region ${REGION} || true
        
        # Add rules to security group
        aws ec2 authorize-security-group-ingress \
            --group-name ${APP_NAME}-sg \
            --protocol tcp \
            --port 22 \
            --cidr 0.0.0.0/0 \
            --region ${REGION} || true
            
        aws ec2 authorize-security-group-ingress \
            --group-name ${APP_NAME}-sg \
            --protocol tcp \
            --port 80 \
            --cidr 0.0.0.0/0 \
            --region ${REGION} || true
            
        aws ec2 authorize-security-group-ingress \
            --group-name ${APP_NAME}-sg \
            --protocol tcp \
            --port 443 \
            --cidr 0.0.0.0/0 \
            --region ${REGION} || true
            
        aws ec2 authorize-security-group-ingress \
            --group-name ${APP_NAME}-sg \
            --protocol tcp \
            --port 8001 \
            --cidr 0.0.0.0/0 \
            --region ${REGION} || true
        
        # Create key pair
        aws ec2 create-key-pair \
            --key-name ${APP_NAME}-key \
            --query 'KeyMaterial' \
            --output text \
            --region ${REGION} > ${APP_NAME}-key.pem
        chmod 400 ${APP_NAME}-key.pem
        
        # User data script for EC2
        cat > ec2-userdata.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y docker git

# Start Docker
service docker start
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository (you'll need to update this with your repo)
cd /home/ec2-user
git clone https://github.com/yourusername/DIYList.git
cd DIYList

# Copy environment file
cp .env.production .env

# Build and run
docker-compose up -d
EOF
        
        # Launch instance
        INSTANCE_ID=$(aws ec2 run-instances \
            --image-id ami-0c02fb55731490381 \
            --instance-type t3.medium \
            --key-name ${APP_NAME}-key \
            --security-groups ${APP_NAME}-sg \
            --user-data file://ec2-userdata.sh \
            --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${APP_NAME}-server}]" \
            --region ${REGION} \
            --query 'Instances[0].InstanceId' \
            --output text)
        
        echo -e "${GREEN}✅ EC2 instance launched: ${INSTANCE_ID}${NC}"
        
        # Wait for instance to be running
        echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
        aws ec2 wait instance-running --instance-ids ${INSTANCE_ID} --region ${REGION}
        
        # Get public IP
        PUBLIC_IP=$(aws ec2 describe-instances \
            --instance-ids ${INSTANCE_ID} \
            --query 'Reservations[0].Instances[0].PublicIpAddress' \
            --output text \
            --region ${REGION})
        
        echo -e "${GREEN}✅ Instance is running at: http://${PUBLIC_IP}${NC}"
        
        # Create S3 bucket for frontend
        echo -e "${YELLOW}📦 Creating S3 bucket for frontend...${NC}"
        BUCKET_NAME="${APP_NAME}-frontend-$(date +%s)"
        
        aws s3 mb s3://${BUCKET_NAME} --region ${REGION}
        
        # Enable static website hosting
        aws s3 website s3://${BUCKET_NAME} \
            --index-document index.html \
            --error-document index.html
        
        # Set bucket policy for public access
        cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF
        
        aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy file://bucket-policy.json
        
        echo -e "${GREEN}✅ S3 bucket created: ${BUCKET_NAME}${NC}"
        
        # Build and upload frontend
        echo -e "${YELLOW}🏗️  Building and uploading frontend...${NC}"
        cd diy-agent-system/frontend
        
        # Update API URL in frontend
        echo "VITE_API_URL=http://${PUBLIC_IP}:8001" > .env.production
        
        npm install
        npm run build
        
        # Upload to S3
        aws s3 sync dist/ s3://${BUCKET_NAME} --acl public-read
        
        echo -e "${GREEN}🎉 Deployment Complete!${NC}"
        echo "=================================="
        echo -e "Backend API: ${BLUE}http://${PUBLIC_IP}:8001${NC}"
        echo -e "Frontend URL: ${BLUE}http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com${NC}"
        echo -e "SSH to server: ${YELLOW}ssh -i ${APP_NAME}-key.pem ec2-user@${PUBLIC_IP}${NC}"
        echo ""
        echo -e "${YELLOW}📝 Next Steps:${NC}"
        echo "1. Set up a custom domain (optional)"
        echo "2. Configure SSL certificate"
        echo "3. Set up monitoring and backups"
        ;;
        
    2)
        echo -e "${BLUE}🏗️  ECS + RDS Deployment coming soon...${NC}"
        echo "This option will set up a production-ready deployment with:"
        echo "- ECS Fargate for auto-scaling backend"
        echo "- RDS PostgreSQL for managed database"
        echo "- Application Load Balancer"
        echo "- CloudFront CDN"
        echo ""
        echo "For now, please use Option 1 or deploy manually using the AWS_DEPLOYMENT_GUIDE.md"
        ;;
        
    3)
        echo -e "${BLUE}🏗️  Serverless Deployment coming soon...${NC}"
        echo "This option will set up a cost-optimized deployment with:"
        echo "- AWS Lambda for backend"
        echo "- API Gateway"
        echo "- DynamoDB or RDS Serverless"
        echo "- S3 + CloudFront for frontend"
        echo ""
        echo "For now, please use Option 1 or deploy manually using the AWS_DEPLOYMENT_GUIDE.md"
        ;;
        
    *)
        echo -e "${RED}❌ Invalid option. Please choose 1, 2, or 3.${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}🚀 AWS Deployment script completed!${NC}"