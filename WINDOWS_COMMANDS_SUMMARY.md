# Windows CMD Commands Summary for cheasydiy.com Deployment

This file contains all the Windows-compatible commands from the deployment guide for easy copy-paste execution.

## Prerequisites

Make sure you have:
- AWS CLI installed and configured
- Docker Desktop running
- Git installed
- Access to your AWS account

## Step 1: AWS Initial Setup

```cmd
# Configure AWS CLI (run interactively)
aws configure

# Get your AWS Account ID
for /f "tokens=*" %i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%i
echo Your AWS Account ID: %AWS_ACCOUNT_ID%

# Create S3 bucket for Terraform state
aws s3 mb s3://cheasydiy-terraform-state --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning --bucket cheasydiy-terraform-state --versioning-configuration Status=Enabled

# Enable encryption
echo {"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]} > encryption.json
aws s3api put-bucket-encryption --bucket cheasydiy-terraform-state --server-side-encryption-configuration file://encryption.json
del encryption.json

# Create DynamoDB table for state locking
aws dynamodb create-table --table-name terraform-state-lock --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --region us-east-1
```

## Step 2: Request SSL Certificates

```cmd
# Request certificate for ALB
aws acm request-certificate --domain-name api.cheasydiy.com --validation-method DNS --region us-east-1

# Request certificate for CloudFront
aws acm request-certificate --domain-name cheasydiy.com --subject-alternative-names "*.cheasydiy.com" "www.cheasydiy.com" --validation-method DNS --region us-east-1

# Check certificate status (replace YOUR_CERTIFICATE_ARN)
aws acm describe-certificate --certificate-arn [YOUR_CERTIFICATE_ARN] --region us-east-1

Hao: aws acm describe-certificate --certificate-arn arn:aws:acm:us-east-1:571600828655:certificate/c2079e43-b693-46cf-be84-94e7c1208be8 --region us-east-1
```

**Important**: Go to AWS Console > Certificate Manager and click "Create records in Route 53" for each certificate.

## Step 3: Create ECR Repositories

```cmd
# Create ECR repositories
aws ecr create-repository --repository-name cheasydiy/backend --image-scanning-configuration scanOnPush=true --region us-east-1
aws ecr create-repository --repository-name cheasydiy/frontend --image-scanning-configuration scanOnPush=true --region us-east-1

# Set lifecycle policy
echo {"rules":[{"rulePriority":1,"description":"Keep last 10 images","selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":10},"action":{"type":"expire"}}]} > lifecycle-policy.json
aws ecr put-lifecycle-policy --repository-name cheasydiy/backend --lifecycle-policy-text file://lifecycle-policy.json --region us-east-1
aws ecr put-lifecycle-policy --repository-name cheasydiy/frontend --lifecycle-policy-text file://lifecycle-policy.json --region us-east-1
del lifecycle-policy.json
```

## Step 4: Build and Push Docker Images

```cmd
# Login to ECR
aws ecr get-login-password --region us-east-1 > ecr_password.txt
set /p ECR_PASSWORD=<ecr_password.txt
echo %ECR_PASSWORD% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com
Hao: May just use 
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 571600828655.dkr.ecr.us-east-1.amazonaws.com
del ecr_password.txt

# Build and push backend
cd diy-agent-system/backend
docker build -t cheasydiy-backend .
docker tag cheasydiy-backend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:latest
docker tag cheasydiy-backend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:v1.0.0
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:latest
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/backend:v1.0.0

# Build and push frontend
cd ../frontend
docker build --build-arg VITE_API_URL=https://api.cheasydiy.com -t cheasydiy-frontend .
docker tag cheasydiy-frontend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:latest
docker tag cheasydiy-frontend:latest %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:v1.0.0
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:latest
docker push %AWS_ACCOUNT_ID%.dkr.ecr.us-east-1.amazonaws.com/cheasydiy/frontend:v1.0.0

cd ../..
```

## Step 5: Configure and Deploy Terraform

```cmd
cd terraform

# Set environment variables for secrets
set TF_VAR_openai_api_key=your-openai-api-key-here
set TF_VAR_jwt_secret_key=your-jwt-secret-key-here
set TF_VAR_db_password=your-db-password-here

# IMPORTANT: Edit terraform/cheasydiy.tfvars file first!
# Update the certificate ARNs from Step 2

# Initialize and deploy
terraform init
terraform plan -var-file="cheasydiy.tfvars"
terraform apply -var-file="cheasydiy.tfvars"
```

## Step 6: Deploy Frontend to S3

```cmd
# Build frontend
cd ../diy-agent-system/frontend
npm install

# Set environment variable for Windows
set VITE_API_URL=https://api.cheasydiy.com
npm run build

# Get S3 bucket and CloudFront info from Terraform
cd ../../terraform
terraform output -raw frontend_s3_bucket > s3_bucket.txt
terraform output -raw cloudfront_distribution_id > cloudfront_id.txt
set /p S3_BUCKET=<s3_bucket.txt
set /p CLOUDFRONT_ID=<cloudfront_id.txt
del s3_bucket.txt cloudfront_id.txt

# Deploy to S3
cd ../diy-agent-system/frontend
aws s3 sync dist/ s3://%S3_BUCKET% --delete --cache-control "public, max-age=31536000" --exclude "index.html" --exclude "*.json"
aws s3 cp dist/index.html s3://%S3_BUCKET%/index.html --cache-control "no-cache, no-store, must-revalidate"
aws s3 cp dist/ s3://%S3_BUCKET%/ --recursive --exclude "*" --include "*.json" --cache-control "no-cache, no-store, must-revalidate"
aws cloudfront create-invalidation --distribution-id %CLOUDFRONT_ID% --paths "/*"
```

## Step 7: Configure Route53 DNS

```cmd
cd F:\DIYList\terraform

  # Get DNS information
  terraform output -raw cloudfront_distribution_domain > cloudfront_domain.txt
  terraform output -raw alb_dns_name > alb_dns.txt

  # Get hosted zone ID (should return just the ID like Z1234567890ABC)
  aws route53 list-hosted-zones-by-name --query "HostedZones[?Name=='cheasydiy.com.'].Id" --output text > hosted_zone.txt

  # Set variables
  set /p CLOUDFRONT_DOMAIN=<cloudfront_domain.txt
  set /p ALB_DNS=<alb_dns.txt
  set /p HOSTED_ZONE_ID=<hosted_zone.txt

  # Verify the values
  echo CloudFront Domain: %CLOUDFRONT_DOMAIN%
  echo ALB DNS: %ALB_DNS%
  echo Hosted Zone ID: %HOSTED_ZONE_ID%

  # Clean up temp files
  del cloudfront_domain.txt alb_dns.txt hosted_zone.txt

  Note:
  - Use %%a in batch files (.bat or .cmd files)
  - Use %a when typing directly in command prompt
  - The simpler approach above avoids the parsing issue entirely

# Create Route53 records
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

aws route53 change-resource-record-sets --hosted-zone-id %HOSTED_ZONE_ID% --change-batch file://route53-records.json
del route53-records.json
```

## Step 8: Test Deployment

```cmd
# Test endpoints (wait 5-10 minutes for DNS propagation first)
curl https://api.cheasydiy.com/api/test
curl -I https://cheasydiy.com
curl -I https://www.cheasydiy.com
```

## Step 9: Set up Monitoring (Optional)

```cmd
# CPU utilization alarm
aws cloudwatch put-metric-alarm --alarm-name cheasydiy-high-cpu --alarm-description "Alert when CPU exceeds 80%" --metric-name CPUUtilization --namespace AWS/ECS --statistic Average --period 300 --threshold 80 --comparison-operator GreaterThanThreshold --dimensions Name=ServiceName,Value=cheasydiy-production-backend Name=ClusterName,Value=cheasydiy-production-cluster

# Auto-scaling setup
aws application-autoscaling register-scalable-target --service-namespace ecs --resource-id service/cheasydiy-production-cluster/cheasydiy-production-backend --scalable-dimension ecs:service:DesiredCount --min-capacity 1 --max-capacity 10

# Billing alarm
aws cloudwatch put-metric-alarm --alarm-name cheasydiy-billing-alarm --alarm-description "Alert when AWS charges exceed $100" --metric-name EstimatedCharges --namespace AWS/Billing --statistic Maximum --period 86400 --threshold 100 --comparison-operator GreaterThanThreshold --dimensions Name=Currency,Value=USD
```

## GitHub Secrets Setup

Go to your GitHub repository > Settings > Secrets and variables > Actions > New repository secret:

```
AWS_ACCESS_KEY_ID = [Your AWS Access Key]
AWS_SECRET_ACCESS_KEY = [Your AWS Secret Key]
AWS_ACCOUNT_ID = [Your AWS Account ID from Step 1]
OPENAI_API_KEY = [Your OpenAI API Key]
VITE_API_URL = https://api.cheasydiy.com
S3_BUCKET_NAME = [S3 bucket name from Terraform output]
CLOUDFRONT_DISTRIBUTION_ID = [CloudFront ID from Terraform output]
```

## Important Notes for Windows Users

1. **Environment Variables**: Use `set VARIABLE=value` instead of `export VARIABLE=value`
2. **File Paths**: Use forward slashes or double backslashes in paths
3. **JSON Files**: Use `echo` commands or create files manually instead of `cat << EOF`
4. **PowerShell Alternative**: You can also run these in PowerShell for better compatibility
5. **Line Breaks**: All commands are on single lines to avoid line continuation issues

## Troubleshooting

If you encounter issues:

1. **Check AWS credentials**: `aws sts get-caller-identity`
2. **Verify Docker is running**: `docker --version`
3. **Check environment variables**: `echo %AWS_ACCOUNT_ID%`
4. **DNS propagation**: Use `nslookup cheasydiy.com` to check DNS

## Next Steps

After successful deployment:
1. Set up CI/CD with GitHub Actions (already configured)
2. Monitor your application in AWS Console
3. Consider adding RDS database for production
4. Set up proper backup strategies

Your application will be available at:
- **Website**: https://cheasydiy.com
- **API**: https://api.cheasydiy.com