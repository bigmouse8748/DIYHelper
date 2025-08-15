# AWS Deployment Guide for DIY Smart Assistant 🚀

**Last Updated**: August 15, 2025  
**Deployment Status**: ✅ **LIVE** at [https://cheasydiy.com](https://cheasydiy.com)

This guide walks you through deploying the DIY Smart Assistant application on AWS using various services.

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- Domain name (optional, for custom domain)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Route 53 (DNS)                       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  CloudFront (CDN)                        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────────────┐                    ┌─────────────────────┐
│  S3 Bucket    │                    │   ALB (Load        │
│  (Frontend)   │                    │   Balancer)        │
└───────────────┘                    └─────────────────────┘
                                              │
                                    ┌─────────────────────┐
                                    │   ECS Fargate      │
                                    │   (Backend API)    │
                                    └─────────────────────┘
                                              │
                                    ┌─────────────────────┐
                                    │   RDS PostgreSQL   │
                                    └─────────────────────┘
```

## 🚀 Deployment Options

### Option 1: Simple Deployment (EC2 + S3)
Best for: Development, testing, small-scale production

### Option 2: Scalable Deployment (ECS + CloudFront)
Best for: Production, high availability, auto-scaling

### Option 3: Serverless Deployment (Lambda + API Gateway)
Best for: Cost optimization, sporadic traffic

---

## 📦 Option 1: Simple Deployment (EC2 + S3)

### Step 1: Deploy Backend on EC2

1. **Launch EC2 Instance**
```bash
# Use Amazon Linux 2 or Ubuntu 22.04 LTS
# Instance type: t3.medium (minimum)
# Security Group: Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8001 (API)
```

2. **SSH into EC2 and Setup Environment**
```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@your-ec2-public-ip

# Update system
sudo yum update -y  # For Amazon Linux
# sudo apt-get update && sudo apt-get upgrade -y  # For Ubuntu

# Install Docker
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install git -y
```

3. **Clone and Deploy Backend**
```bash
# Clone repository
git clone https://github.com/bigmouse8748/DIYHelper.git
cd DIYHelper/diy-agent-system/backend

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_api_key_here
JWT_SECRET_KEY=your_jwt_secret_here
DATABASE_URL=postgresql://user:pass@localhost:5432/diydb
CORS_ORIGINS=https://your-domain.com
EOF

# Build and run with Docker
docker build -t diy-backend .
docker run -d \
  --name diy-backend \
  -p 8001:8001 \
  --env-file .env \
  --restart unless-stopped \
  diy-backend
```

### Step 2: Deploy Frontend on S3

1. **Build Frontend Locally**
```bash
cd diy-agent-system/frontend

# Update API endpoint in environment
echo "VITE_API_URL=http://your-ec2-public-ip:8001" > .env.production

# Build for production
npm install
npm run build
```

2. **Create S3 Bucket and Deploy**
```bash
# Create S3 bucket
aws s3 mb s3://your-diy-assistant-frontend

# Enable static website hosting
aws s3 website s3://your-diy-assistant-frontend \
  --index-document index.html \
  --error-document index.html

# Upload build files
aws s3 sync dist/ s3://your-diy-assistant-frontend --acl public-read

# Set bucket policy for public access
aws s3api put-bucket-policy --bucket your-diy-assistant-frontend --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-diy-assistant-frontend/*"
    }
  ]
}'
```

---

## 🚢 Option 2: Scalable Deployment (ECS + CloudFront)

### Step 1: Containerize Application

Create Docker files (already included in the next section)

### Step 2: Push to ECR

```bash
# Create ECR repositories
aws ecr create-repository --repository-name diy-backend
aws ecr create-repository --repository-name diy-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build and push images
docker build -t diy-backend ./backend
docker tag diy-backend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/diy-backend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/diy-backend:latest
```

### Step 3: Create ECS Task Definition

```json
{
  "family": "diy-assistant-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/diy-backend:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "CORS_ORIGINS", "value": "https://your-domain.com"}
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        },
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:jwt-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/diy-assistant",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

### Step 4: Create ECS Service

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name diy-assistant-cluster

# Create service
aws ecs create-service \
  --cluster diy-assistant-cluster \
  --service-name diy-backend-service \
  --task-definition diy-assistant-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Step 5: Setup Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name diy-assistant-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name diy-backend-targets \
  --protocol HTTP \
  --port 8001 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /api/test

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### Step 6: Setup CloudFront for Frontend

```bash
# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config '{
  "CallerReference": "diy-assistant-2024",
  "Origins": {
    "Items": [
      {
        "Id": "S3-diy-frontend",
        "DomainName": "your-diy-assistant-frontend.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      },
      {
        "Id": "ALB-backend",
        "DomainName": "diy-assistant-alb.us-east-1.elb.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultRootObject": "index.html",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-diy-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": ["GET", "HEAD"],
    "CachedMethods": ["GET", "HEAD"],
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    }
  },
  "CacheBehaviors": {
    "Items": [
      {
        "PathPattern": "/api/*",
        "TargetOriginId": "ALB-backend",
        "ViewerProtocolPolicy": "https-only",
        "AllowedMethods": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
        "ForwardedValues": {
          "QueryString": true,
          "Headers": ["*"],
          "Cookies": {"Forward": "all"}
        }
      }
    ]
  }
}'
```

---

## 🔧 Option 3: Serverless Deployment (Lambda + API Gateway)

### Step 1: Convert Backend to Lambda Functions

Create `lambda_handler.py`:
```python
from mangum import Mangum
from main_enhanced import app

handler = Mangum(app)
```

### Step 2: Deploy with SAM or Serverless Framework

Create `template.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  DIYAssistantAPI:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/
      Handler: lambda_handler.handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 512
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseUrl
          OPENAI_API_KEY: !Ref OpenAIKey
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

Deploy:
```bash
sam build
sam deploy --guided
```

---

## 🗄️ Database Setup (RDS)

### Create RDS PostgreSQL Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier diy-assistant-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username dbadmin \
  --master-user-password yourpassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx \
  --backup-retention-period 7 \
  --no-publicly-accessible
```

### Initialize Database

```sql
-- Connect to RDS instance and run
CREATE DATABASE diy_assistant;

-- Create tables (run from backend)
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

---

## 🔐 Security Best Practices

### 1. Use AWS Secrets Manager
```bash
# Store secrets
aws secretsmanager create-secret \
  --name diy-assistant/openai-key \
  --secret-string "your-openai-api-key"

aws secretsmanager create-secret \
  --name diy-assistant/jwt-secret \
  --secret-string "your-jwt-secret"
```

### 2. Setup SSL/TLS
```bash
# Request ACM certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS \
  --subject-alternative-names "*.your-domain.com"
```

### 3. Configure WAF
```bash
# Create Web ACL for CloudFront
aws wafv2 create-web-acl \
  --name diy-assistant-waf \
  --scope CLOUDFRONT \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

---

## 📊 Monitoring & Logging

### CloudWatch Setup
```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name DIYAssistant \
  --dashboard-body file://dashboard.json

# Set up alarms
aws cloudwatch put-metric-alarm \
  --alarm-name high-api-latency \
  --alarm-description "Alert when API latency is too high" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 3000 \
  --comparison-operator GreaterThanThreshold
```

---

## 💰 Cost Optimization Tips

1. **Use Spot Instances for ECS tasks** (up to 90% savings)
2. **Enable S3 Intelligent-Tiering** for automatic cost optimization
3. **Use CloudFront caching** to reduce backend calls
4. **Set up auto-scaling** based on actual usage
5. **Use Reserved Instances** for predictable workloads

### Estimated Monthly Costs

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| EC2 | t3.medium (1 instance) | $30 |
| S3 | 10GB storage + 100GB transfer | $5 |
| RDS | db.t3.micro | $15 |
| CloudFront | 100GB transfer | $8 |
| ECS Fargate | 2 tasks (0.5 vCPU, 1GB) | $35 |
| **Total** | | **~$93/month** |

---

## 🚦 CI/CD Pipeline

See the GitHub Actions workflow in `.github/workflows/aws-deploy.yml` for automated deployment.

---

## 📱 Custom Domain Setup

1. **Register domain in Route 53**
2. **Create hosted zone**
3. **Update CloudFront distribution**
4. **Create Route 53 alias records**

```bash
# Create A record pointing to CloudFront
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXX \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "your-domain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "dxxxxx.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

---

## 🆘 Troubleshooting

### Common Issues

1. **CORS errors**: Check CORS_ORIGINS environment variable
2. **Database connection**: Verify security groups and RDS endpoint
3. **High latency**: Enable CloudFront caching, check Lambda cold starts
4. **Deployment failures**: Check IAM permissions, resource limits

### Useful Commands

```bash
# View ECS logs
aws logs tail /ecs/diy-assistant --follow

# Check ECS service status
aws ecs describe-services --cluster diy-assistant-cluster --services diy-backend-service

# Test API endpoint
curl https://api.your-domain.com/api/test

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id EXXXXX --paths "/*"
```

---

## 📚 Additional Resources

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)

---

**Need help?** Create an issue in the [GitHub repository](https://github.com/bigmouse8748/DIYHelper/issues)