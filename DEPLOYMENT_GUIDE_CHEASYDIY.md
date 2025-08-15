# Step-by-Step AWS Deployment Guide for cheasydiy.com

This guide will walk you through deploying your DIY Smart Assistant to AWS using ECS + CloudFront with your domain cheasydiy.com.

## 📋 Prerequisites Checklist

- [ ] AWS Account with administrative access
- [ ] AWS CLI installed and configured
- [ ] Docker Desktop installed
- [ ] Domain cheasydiy.com registered in Route53
- [ ] GitHub repository ready
- [ ] Local development environment working

## Step 1: AWS Initial Setup 🔧

### 1.1 Configure AWS CLI
```bash
aws configure
# Enter:
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: us-east-1
# Default output format: json
```

### 1.2 Get Your AWS Account ID
```bash
aws sts get-caller-identity --query Account --output text
# Save this number, you'll need it multiple times
```

### 1.3 Create S3 Bucket for Terraform State
```bash
# Create bucket for Terraform state
aws s3 mb s3://cheasydiy-terraform-state --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning --bucket cheasydiy-terraform-state --versioning-configuration Status=Enabled

# Enable encryption (create encryption.json first)
echo {"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]} > encryption.json
aws s3api put-bucket-encryption --bucket cheasydiy-terraform-state --server-side-encryption-configuration file://encryption.json
del encryption.json

# Create DynamoDB table for state locking
aws dynamodb create-table --table-name terraform-state-lock --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --region us-east-1
```

## Step 2: SSL Certificates Setup 🔒

### 2.1 Request Certificate for ALB (in us-east-1)
```bash
# Request certificate for ALB
aws acm request-certificate --domain-name api.cheasydiy.com --validation-method DNS --region us-east-1

REM Note the CertificateArn that's returned
REM Example: arn:aws:acm:us-east-1:123456789012:certificate/abc-123-def
```

### 2.2 Request Certificate for CloudFront (MUST be in us-east-1)
```bash
# Request certificate for CloudFront
aws acm request-certificate --domain-name cheasydiy.com --subject-alternative-names "*.cheasydiy.com" "www.cheasydiy.com" --validation-method DNS --region us-east-1

REM Note this CertificateArn as well
```

### 2.3 Validate Certificates in Route53
```bash
# Go to AWS Console > Certificate Manager
# For each certificate:
# 1. Click on the certificate
# 2. Click "Create records in Route 53"
# 3. Wait for validation (5-10 minutes)

# Or check status via CLI (replace YOUR_CERTIFICATE_ARN):
aws acm describe-certificate --certificate-arn [YOUR_CERTIFICATE_ARN] --region us-east-1
```

## Step 3: Create ECR Repositories 📦

```bash
# Set your account ID as a variable (Windows CMD)
for /f "tokens=*" %i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%i

# Create ECR repositories
aws ecr create-repository --repository-name cheasydiy/backend --image-scanning-configuration scanOnPush=true --region us-east-1

aws ecr create-repository --repository-name cheasydiy/frontend --image-scanning-configuration scanOnPush=true --region us-east-1

# Set lifecycle policy to keep only last 10 images (create policy file first)
echo {"rules":[{"rulePriority":1,"description":"Keep last 10 images","selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":10},"action":{"type":"expire"}}]} > lifecycle-policy.json

aws ecr put-lifecycle-policy --repository-name cheasydiy/backend --lifecycle-policy-text file://lifecycle-policy.json --region us-east-1

# Same for frontend
aws ecr put-lifecycle-policy --repository-name cheasydiy/frontend --lifecycle-policy-text file://lifecycle-policy.json --region us-east-1

# Clean up
del lifecycle-policy.json
```

## Step 4: Build and Push Docker Images 🐳

### 4.1 Login to ECR
```bash
# Login to ECR (Windows CMD - run one at a time)
aws ecr get-login-password --region us-east-1 > ecr_password.txt
set /p ECR_PASSWORD=<ecr_password.txt
echo %ECR_PASSWORD% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com
del ecr_password.txt
```

### 4.2 Build and Push Backend
```bash
cd diy-agent-system/backend

# Build backend image
docker build -t cheasydiy-backend .

# Tag for ECR
docker tag cheasydiy-backend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:latest

docker tag cheasydiy-backend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:v1.0.0

# Push to ECR
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:latest
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:v1.0.0
```

### 4.3 Build and Push Frontend
```bash
cd ../frontend

# Build frontend with production API URL
docker build --build-arg VITE_API_URL=https://api.cheasydiy.com -t cheasydiy-frontend .

# Tag for ECR
docker tag cheasydiy-frontend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:latest

docker tag cheasydiy-frontend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:v1.0.0

# Push to ECR
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:latest
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:v1.0.0

cd ../..
```

## Step 5: Configure Terraform 🏗️

### 5.1 Update Terraform Backend Configuration
```bash
cd terraform

# Update main.tf backend configuration
# The backend block should reference your S3 bucket:
# backend "s3" {
#   bucket = "cheasydiy-terraform-state"
#   key    = "infrastructure/terraform.tfstate"
#   region = "us-east-1"
#   encrypt = true
#   dynamodb_table = "terraform-state-lock"
# }
```

### 5.2 Create terraform.tfvars
```bash
cat > terraform.tfvars << 'EOF'
# AWS Configuration
aws_region = "us-east-1"

# Project Configuration
project_name = "cheasydiy"
environment  = "production"

# Domain Configuration
domain_name = "cheasydiy.com"

# Get these from Step 2
certificate_arn            = "arn:aws:acm:us-east-1:YOUR_ACCOUNT:certificate/YOUR_ALB_CERT_ID"
cloudfront_certificate_arn = "arn:aws:acm:us-east-1:YOUR_ACCOUNT:certificate/YOUR_CF_CERT_ID"

# Network Configuration
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]

# ECS Configuration - Backend
backend_task_cpu      = "512"
backend_task_memory   = "1024"
backend_desired_count = 2
backend_min_capacity  = 1
backend_max_capacity  = 4
backend_image_tag     = "v1.0.0"

# Frontend Deployment
deploy_frontend_to_s3  = true
deploy_frontend_to_ecs = false

# Database (start without, add later)
enable_rds = false

# Redis (start without, add later)
enable_redis = false

# Security
enable_encryption = true

# Application Configuration
cors_origins = "https://cheasydiy.com,https://www.cheasydiy.com,https://api.cheasydiy.com"

# Backend Environment Variables
backend_environment_variables = {
  ENVIRONMENT = "production"
  LOG_LEVEL   = "INFO"
}
EOF
```

### 5.3 Set Sensitive Variables
```bash
# Set sensitive variables via environment (Windows CMD)
set TF_VAR_openai_api_key=your-openai-api-key
set TF_VAR_jwt_secret_key=YOUR_JWT_SECRET_HERE
set TF_VAR_db_password=YOUR_DB_PASSWORD_HERE

REM To generate random keys on Windows, use PowerShell:
REM powershell -Command "[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((1..32 | ForEach {[char](Get-Random -Min 65 -Max 90)})))"
```

### 5.4 Initialize and Deploy Terraform
```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# If everything looks good, deploy!
terraform apply

# This will take 10-15 minutes
# Save the outputs, especially:
# - alb_dns_name
# - cloudfront_distribution_domain
# - s3_bucket_name
```

## Step 6: Deploy Frontend to S3 + CloudFront 🌐

### 6.1 Build Frontend for Production
```bash
cd ../diy-agent-system/frontend

# Create production build
npm install
VITE_API_URL=https://api.cheasydiy.com npm run build
```

### 6.2 Get S3 Bucket Name from Terraform
```bash
cd ../../terraform
terraform output -raw frontend_s3_bucket > s3_bucket.txt
terraform output -raw cloudfront_distribution_id > cloudfront_id.txt
set /p S3_BUCKET=<s3_bucket.txt
set /p CLOUDFRONT_ID=<cloudfront_id.txt
del s3_bucket.txt cloudfront_id.txt
```

### 6.3 Deploy to S3
```bash
cd ../diy-agent-system/frontend

# Sync build files to S3
aws s3 sync dist/ s3://%S3_BUCKET% --delete --cache-control "public, max-age=31536000" --exclude "index.html" --exclude "*.json"

# Upload index.html with no-cache
aws s3 cp dist/index.html s3://%S3_BUCKET%/index.html --cache-control "no-cache, no-store, must-revalidate"

# Upload JSON files with no-cache
aws s3 cp dist/ s3://%S3_BUCKET%/ --recursive --exclude "*" --include "*.json" --cache-control "no-cache, no-store, must-revalidate"

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id %CLOUDFRONT_ID% --paths "/*"
```

## Step 7: Configure Route53 🌍

### 7.1 Get your CloudFront and ALB endpoints
```bash
cd ../../terraform

# Get the values (Windows CMD)
terraform output -raw cloudfront_distribution_domain > cloudfront_domain.txt
terraform output -raw alb_dns_name > alb_dns.txt
aws route53 list-hosted-zones-by-name --query "HostedZones[?Name=='cheasydiy.com.'].Id" --output text > hosted_zone.txt

set /p CLOUDFRONT_DOMAIN=<cloudfront_domain.txt
set /p ALB_DNS=<alb_dns.txt
set /p HOSTED_ZONE_FULL=<hosted_zone.txt

REM Extract zone ID from full path (remove /hostedzone/ prefix)
for /f "tokens=3 delims=/" %%a in ("%HOSTED_ZONE_FULL%") do set HOSTED_ZONE_ID=%%a

del cloudfront_domain.txt alb_dns.txt hosted_zone.txt
```

### 7.2 Create Route53 Records
```bash
# Create a JSON file for the DNS records (Windows CMD)
(
echo {
echo   "Changes": [
echo     {
echo       "Action": "UPSERT",
echo       "ResourceRecordSet": {
echo         "Name": "cheasydiy.com",
echo         "Type": "A",
echo         "AliasTarget": {
echo           "HostedZoneId": "Z2FDTNDATAQYW2",
echo           "DNSName": "%CLOUDFRONT_DOMAIN%",
echo           "EvaluateTargetHealth": false
echo         }
echo       }
echo     },
echo     {
echo       "Action": "UPSERT",
echo       "ResourceRecordSet": {
echo         "Name": "www.cheasydiy.com",
echo         "Type": "A",
echo         "AliasTarget": {
echo           "HostedZoneId": "Z2FDTNDATAQYW2",
echo           "DNSName": "%CLOUDFRONT_DOMAIN%",
echo           "EvaluateTargetHealth": false
echo         }
echo       }
echo     },
echo     {
echo       "Action": "UPSERT",
echo       "ResourceRecordSet": {
echo         "Name": "api.cheasydiy.com",
echo         "Type": "A",
echo         "AliasTarget": {
echo           "HostedZoneId": "Z35SXDOTRQ7X7K",
echo           "DNSName": "%ALB_DNS%",
echo           "EvaluateTargetHealth": true
echo         }
echo       }
echo     }
echo   ]
echo }
) > route53-records.json

# Apply the DNS changes
aws route53 change-resource-record-sets --hosted-zone-id %HOSTED_ZONE_ID% --change-batch file://route53-records.json

# Clean up
del route53-records.json
```

## Step 8: Set Up GitHub Actions CI/CD 🚀

### 8.1 Create GitHub Secrets
Go to your GitHub repository > Settings > Secrets and add:

```bash
# Required secrets:
AWS_ACCESS_KEY_ID         # Your AWS access key
AWS_SECRET_ACCESS_KEY     # Your AWS secret key
AWS_ACCOUNT_ID           # Your AWS account ID
OPENAI_API_KEY          # Your OpenAI API key
VITE_API_URL            # https://api.cheasydiy.com
S3_BUCKET_NAME          # Frontend S3 bucket name
CLOUDFRONT_DISTRIBUTION_ID # CloudFront distribution ID
```

### 8.2 Update GitHub Actions Workflow
```bash
cd ../..

# Update the GitHub Actions file with your values
cat > .github/workflows/deploy-production.yml << 'EOF'
name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY_BACKEND: cheasydiy/backend
  ECR_REPOSITORY_FRONTEND: cheasydiy/frontend
  ECS_CLUSTER: cheasydiy-production-cluster
  ECS_SERVICE_BACKEND: cheasydiy-production-backend
  ECS_TASK_DEFINITION_BACKEND: cheasydiy-production-backend

jobs:
  deploy:
    name: Deploy to AWS
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    # Backend deployment
    - name: Build and push backend
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        cd diy-agent-system/backend
        docker build -t $ECR_REGISTRY/${{ env.ECR_REPOSITORY_BACKEND }}:$IMAGE_TAG .
        docker push $ECR_REGISTRY/${{ env.ECR_REPOSITORY_BACKEND }}:$IMAGE_TAG
        docker tag $ECR_REGISTRY/${{ env.ECR_REPOSITORY_BACKEND }}:$IMAGE_TAG \
          $ECR_REGISTRY/${{ env.ECR_REPOSITORY_BACKEND }}:latest
        docker push $ECR_REGISTRY/${{ env.ECR_REPOSITORY_BACKEND }}:latest

    - name: Update ECS service
      run: |
        aws ecs update-service \
          --cluster ${{ env.ECS_CLUSTER }} \
          --service ${{ env.ECS_SERVICE_BACKEND }} \
          --force-new-deployment

    # Frontend deployment
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: diy-agent-system/frontend/package-lock.json

    - name: Build frontend
      env:
        VITE_API_URL: ${{ secrets.VITE_API_URL }}
      run: |
        cd diy-agent-system/frontend
        npm ci
        npm run build

    - name: Deploy to S3
      run: |
        cd diy-agent-system/frontend
        aws s3 sync dist/ s3://${{ secrets.S3_BUCKET_NAME }} \
          --delete \
          --cache-control "public, max-age=31536000" \
          --exclude "index.html"
        
        aws s3 cp dist/index.html s3://${{ secrets.S3_BUCKET_NAME }}/index.html \
          --cache-control "no-cache, no-store, must-revalidate"

    - name: Invalidate CloudFront
      run: |
        aws cloudfront create-invalidation \
          --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
          --paths "/*"

    - name: Wait for deployment
      run: |
        aws ecs wait services-stable \
          --cluster ${{ env.ECS_CLUSTER }} \
          --services ${{ env.ECS_SERVICE_BACKEND }}
        echo "✅ Deployment completed successfully!"
EOF
```

## Step 9: Test Your Deployment 🧪

### 9.1 Test the endpoints
```bash
# Test backend health
curl https://api.cheasydiy.com/api/test

# Test frontend
curl -I https://cheasydiy.com

# Test www redirect
curl -I https://www.cheasydiy.com
```

### 9.2 Monitor in AWS Console
1. **ECS**: Check cluster > services > tasks are running
2. **CloudWatch**: Check logs for any errors
3. **ALB**: Check target health
4. **CloudFront**: Check distribution status

### 9.3 Test the full application
1. Open https://cheasydiy.com in your browser
2. Upload an image
3. Check if analysis works
4. Test language switching

## Step 10: Post-Deployment Setup 🔧

### 10.1 Set up CloudWatch Alarms
```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm --alarm-name cheasydiy-high-cpu --alarm-description "Alert when CPU exceeds 80%" --metric-name CPUUtilization --namespace AWS/ECS --statistic Average --period 300 --threshold 80 --comparison-operator GreaterThanThreshold --dimensions Name=ServiceName,Value=cheasydiy-production-backend Name=ClusterName,Value=cheasydiy-production-cluster

# ALB unhealthy targets alarm
aws cloudwatch put-metric-alarm --alarm-name cheasydiy-unhealthy-targets --alarm-description "Alert when targets are unhealthy" --metric-name UnHealthyHostCount --namespace AWS/ApplicationELB --statistic Average --period 60 --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold
```

### 10.2 Enable Auto-scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target --service-namespace ecs --resource-id service/cheasydiy-production-cluster/cheasydiy-production-backend --scalable-dimension ecs:service:DesiredCount --min-capacity 1 --max-capacity 10

# Create scaling policy (create policy file first)
echo {"TargetValue":70.0,"PredefinedMetricSpecification":{"PredefinedMetricType":"ECSServiceAverageCPUUtilization"},"ScaleOutCooldown":60,"ScaleInCooldown":60} > scaling-policy.json

aws application-autoscaling put-scaling-policy --service-namespace ecs --resource-id service/cheasydiy-production-cluster/cheasydiy-production-backend --scalable-dimension ecs:service:DesiredCount --policy-name cheasydiy-cpu-scaling --policy-type TargetTrackingScaling --target-tracking-scaling-policy-configuration file://scaling-policy.json

del scaling-policy.json
```

## 🎉 Deployment Complete!

Your DIY Smart Assistant is now live at:
- **Website**: https://cheasydiy.com
- **API**: https://api.cheasydiy.com
- **WWW**: https://www.cheasydiy.com (redirects to main)

## 📊 Monitoring Dashboard

Access these AWS services to monitor your application:
- **CloudWatch**: Logs and metrics
- **ECS Console**: Container status
- **ALB**: Target health
- **CloudFront**: CDN metrics
- **Route53**: DNS health checks

## 🚨 Troubleshooting

### If the site doesn't load:
1. Check CloudFront distribution status (should be "Deployed")
2. Verify Route53 records are propagated (can take up to 48 hours)
3. Check ALB target health
4. Review ECS task logs in CloudWatch

### If API calls fail:
1. Check CORS settings in backend
2. Verify ALB security groups allow traffic
3. Check ECS task logs
4. Verify environment variables are set correctly

## 💰 Cost Monitoring

Set up a billing alarm:
```bash
aws cloudwatch put-metric-alarm --alarm-name cheasydiy-billing-alarm --alarm-description "Alert when AWS charges exceed $100" --metric-name EstimatedCharges --namespace AWS/Billing --statistic Maximum --period 86400 --threshold 100 --comparison-operator GreaterThanThreshold --dimensions Name=Currency,Value=USD
```

## 🔄 Future Updates

When you push to main branch, GitHub Actions will automatically:
1. Build new Docker images
2. Push to ECR
3. Update ECS service
4. Deploy frontend to S3
5. Invalidate CloudFront cache

## 📝 Next Steps

1. **Add RDS Database**: Set `enable_rds = true` in terraform.tfvars
2. **Add Redis Cache**: Set `enable_redis = true` in terraform.tfvars
3. **Enable Cognito**: For user authentication
4. **Set up Backups**: Enable automated backups for RDS
5. **Add Monitoring**: Set up detailed CloudWatch dashboards

---

Congratulations! Your DIY Smart Assistant is now running on AWS with enterprise-grade infrastructure! 🎊