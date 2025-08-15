#!/bin/bash

# DIY Smart Assistant - Migration to Existing AWS Infrastructure
# This script helps deploy to your existing AWS setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 DIY Smart Assistant - AWS Migration Script${NC}"
echo "================================================="

# Get existing infrastructure info
echo -e "${YELLOW}📋 Let's identify your existing AWS infrastructure...${NC}"

read -p "Do you have an existing EC2 instance? (y/n): " HAS_EC2
read -p "Do you have an existing RDS database? (y/n): " HAS_RDS
read -p "Do you have an existing S3 bucket for frontend? (y/n): " HAS_S3
read -p "Do you have an existing domain/CloudFront? (y/n): " HAS_DOMAIN

if [ "$HAS_EC2" = "y" ]; then
    read -p "Enter your EC2 instance ID: " EC2_INSTANCE_ID
    read -p "Enter your EC2 key pair name: " EC2_KEY_NAME
    
    # Get EC2 details
    EC2_IP=$(aws ec2 describe-instances \
        --instance-ids $EC2_INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    echo -e "${GREEN}✅ Found EC2 instance: $EC2_INSTANCE_ID ($EC2_IP)${NC}"
fi

if [ "$HAS_RDS" = "y" ]; then
    read -p "Enter your RDS instance identifier: " RDS_INSTANCE_ID
    read -p "Enter your RDS username: " RDS_USERNAME
    read -p "Enter your RDS password: " RDS_PASSWORD
    read -p "Enter your RDS database name: " RDS_DB_NAME
    
    # Get RDS endpoint
    RDS_ENDPOINT=$(aws rds describe-db-instances \
        --db-instance-identifier $RDS_INSTANCE_ID \
        --query 'DBInstances[0].Endpoint.Address' \
        --output text)
    
    echo -e "${GREEN}✅ Found RDS instance: $RDS_INSTANCE_ID ($RDS_ENDPOINT)${NC}"
fi

if [ "$HAS_S3" = "y" ]; then
    read -p "Enter your S3 bucket name for frontend: " S3_BUCKET_NAME
    echo -e "${GREEN}✅ Will use S3 bucket: $S3_BUCKET_NAME${NC}"
fi

if [ "$HAS_DOMAIN" = "y" ]; then
    read -p "Enter your domain name: " DOMAIN_NAME
    read -p "Enter your CloudFront distribution ID (if any): " CLOUDFRONT_ID
    echo -e "${GREEN}✅ Will use domain: $DOMAIN_NAME${NC}"
fi

# Get application configuration
echo -e "${YELLOW}🔧 Application Configuration${NC}"
read -p "Enter your OpenAI API key: " OPENAI_API_KEY
read -p "Enter a JWT secret key (or press Enter to generate): " JWT_SECRET

if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -hex 32)
    echo "Generated JWT secret: $JWT_SECRET"
fi

# Create production environment configuration
echo -e "${YELLOW}📄 Creating production environment configuration...${NC}"

if [ "$HAS_RDS" = "y" ]; then
    DATABASE_URL="postgresql://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_ENDPOINT}:5432/${RDS_DB_NAME}"
else
    DATABASE_URL="sqlite:///./production.db"
fi

if [ "$HAS_DOMAIN" = "y" ]; then
    CORS_ORIGINS="https://${DOMAIN_NAME},https://www.${DOMAIN_NAME}"
    API_URL="https://api.${DOMAIN_NAME}"
else
    CORS_ORIGINS="http://${EC2_IP}:8001,http://${EC2_IP}"
    API_URL="http://${EC2_IP}:8001"
fi

# Create .env.production file
cat > .env.production << EOF
# Production Environment Configuration for Existing AWS
DATABASE_URL=${DATABASE_URL}
JWT_SECRET_KEY=${JWT_SECRET}
OPENAI_API_KEY=${OPENAI_API_KEY}
ADMIN_SETUP_KEY=setup_admin_prod_2025
AWS_REGION=us-east-1
CORS_ORIGINS=${CORS_ORIGINS}
ENVIRONMENT=production

# Optional AWS services
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
S3_BUCKET=${S3_BUCKET_NAME:-}
EOF

echo -e "${GREEN}✅ Environment configuration created${NC}"

# Deploy to EC2 if available
if [ "$HAS_EC2" = "y" ]; then
    echo -e "${YELLOW}🚀 Deploying to existing EC2 instance...${NC}"
    
    # Create deployment package
    echo "Creating deployment package..."
    tar -czf diy-app-deployment.tar.gz \
        diy-agent-system/ \
        docker-compose.yml \
        .env.production \
        --exclude=node_modules \
        --exclude=.git \
        --exclude=__pycache__ \
        --exclude=*.pyc
    
    # Upload to EC2
    echo "Uploading to EC2..."
    scp -i ${EC2_KEY_NAME}.pem diy-app-deployment.tar.gz ec2-user@${EC2_IP}:/home/ec2-user/
    
    # Deploy on EC2
    echo "Deploying on EC2..."
    ssh -i ${EC2_KEY_NAME}.pem ec2-user@${EC2_IP} << 'ENDSSH'
# Extract deployment package
cd /home/ec2-user
tar -xzf diy-app-deployment.tar.gz

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo usermod -a -G docker ec2-user
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Stop existing containers if any
docker-compose down 2>/dev/null || true

# Copy environment file
cp .env.production .env

# Build and start the application
docker-compose up --build -d

# Check if containers are running
docker-compose ps

echo "✅ Application deployed successfully!"
echo "Backend API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8001"
echo "Health check: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8001/api/test"
ENDSSH
    
    echo -e "${GREEN}✅ Backend deployed to EC2${NC}"
fi

# Deploy frontend to S3 if available
if [ "$HAS_S3" = "y" ]; then
    echo -e "${YELLOW}🌐 Deploying frontend to existing S3 bucket...${NC}"
    
    cd diy-agent-system/frontend
    
    # Create frontend environment
    echo "VITE_API_URL=${API_URL}" > .env.production
    
    # Install dependencies and build
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    echo "Building frontend..."
    npm run build
    
    # Upload to S3
    echo "Uploading to S3..."
    aws s3 sync dist/ s3://${S3_BUCKET_NAME} --delete --acl public-read
    
    # Invalidate CloudFront if available
    if [ "$HAS_DOMAIN" = "y" ] && [ ! -z "$CLOUDFRONT_ID" ]; then
        echo "Invalidating CloudFront cache..."
        aws cloudfront create-invalidation \
            --distribution-id ${CLOUDFRONT_ID} \
            --paths "/*"
    fi
    
    cd ../..
    echo -e "${GREEN}✅ Frontend deployed to S3${NC}"
fi

# Initialize database if RDS is available
if [ "$HAS_RDS" = "y" ]; then
    echo -e "${YELLOW}🗄️ Initializing database...${NC}"
    
    if [ "$HAS_EC2" = "y" ]; then
        ssh -i ${EC2_KEY_NAME}.pem ec2-user@${EC2_IP} << ENDSSH
# Run database initialization
docker-compose exec backend python -c "
from database import create_tables, test_connection
try:
    if test_connection():
        print('✅ Database connection successful')
        create_tables()
        print('✅ Database tables created')
    else:
        print('❌ Database connection failed')
except Exception as e:
    print(f'Database setup error: {e}')
"
ENDSSH
    fi
    
    echo -e "${GREEN}✅ Database initialized${NC}"
fi

# Cleanup
rm -f diy-app-deployment.tar.gz 2>/dev/null || true

echo -e "${GREEN}🎉 Migration to existing AWS infrastructure completed!${NC}"
echo "========================================================"

if [ "$HAS_EC2" = "y" ]; then
    echo -e "Backend API: ${BLUE}${API_URL}${NC}"
    echo -e "Health Check: ${BLUE}${API_URL}/api/test${NC}"
fi

if [ "$HAS_S3" = "y" ] && [ "$HAS_DOMAIN" = "y" ]; then
    echo -e "Frontend: ${BLUE}https://${DOMAIN_NAME}${NC}"
elif [ "$HAS_S3" = "y" ]; then
    echo -e "Frontend: ${BLUE}http://${S3_BUCKET_NAME}.s3-website-us-east-1.amazonaws.com${NC}"
fi

echo -e "Admin Login: ${YELLOW}admin / Admin123!${NC}"

echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Test the application URLs above"
echo "2. Check that all services are running properly"
echo "3. Set up monitoring and alerts if needed"
echo "4. Configure automatic backups"

if [ "$HAS_RDS" != "y" ]; then
    echo "5. Consider migrating to RDS for production database"
fi

if [ "$HAS_DOMAIN" != "y" ]; then
    echo "5. Set up a custom domain and SSL certificate"
fi