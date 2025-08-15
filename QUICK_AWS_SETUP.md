# 🚀 Quick AWS Deployment Guide

This guide will get your DIY Smart Assistant running on AWS in about 15-20 minutes.

## Prerequisites

✅ AWS Account  
✅ AWS CLI installed (`pip install awscli`)  
✅ Docker installed  
✅ Domain name (optional)  

## Option 1: Automated Script (Easiest)

```bash
# Make the script executable
chmod +x deploy-to-aws.sh

# Run the deployment script
./deploy-to-aws.sh
```

The script will:
1. ✅ Check prerequisites
2. 🏗️ Launch an EC2 instance with Docker
3. 📦 Create an S3 bucket for frontend
4. 🚀 Deploy your application
5. 🌐 Give you URLs to access your app

## Option 2: Manual Quick Setup

### Step 1: Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Default region: us-east-1
# Default output format: json
```

### Step 2: Launch EC2 Instance
```bash
# Create security group
aws ec2 create-security-group \
    --group-name diy-sg \
    --description "DIY Assistant Security Group"

# Add rules
aws ec2 authorize-security-group-ingress --group-name diy-sg --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name diy-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name diy-sg --protocol tcp --port 8001 --cidr 0.0.0.0/0

# Create key pair
aws ec2 create-key-pair --key-name diy-key --query 'KeyMaterial' --output text > diy-key.pem
chmod 400 diy-key.pem

# Launch instance (replace ami-xxx with latest Amazon Linux 2 AMI)
aws ec2 run-instances \
    --image-id ami-0c02fb55731490381 \
    --instance-type t3.medium \
    --key-name diy-key \
    --security-groups diy-sg \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=diy-server}]'
```

### Step 3: SSH and Setup
```bash
# Get instance public IP
INSTANCE_IP=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=diy-server" --query "Reservations[*].Instances[*].PublicIpAddress" --output text)

# SSH into instance
ssh -i diy-key.pem ec2-user@$INSTANCE_IP

# On the server:
sudo yum update -y
sudo yum install -y docker git
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone your repository
git clone https://github.com/yourusername/DIYList.git
cd DIYList

# Create environment file
cat > .env << EOF
OPENAI_API_KEY=your-api-key-here
JWT_SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./production.db
CORS_ORIGINS=http://$INSTANCE_IP
EOF

# Run with Docker
docker-compose up -d
```

### Step 4: Create S3 Bucket for Frontend
```bash
# From your local machine
BUCKET_NAME="diy-frontend-$(date +%s)"

aws s3 mb s3://$BUCKET_NAME
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

# Set bucket policy for public access
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

# Build and upload frontend
cd diy-agent-system/frontend
echo "VITE_API_URL=http://$INSTANCE_IP:8001" > .env.production
npm install
npm run build
aws s3 sync dist/ s3://$BUCKET_NAME --acl public-read
```

## 🎉 Your App is Live!

- **Backend API**: `http://YOUR_INSTANCE_IP:8001`
- **Frontend**: `http://YOUR_BUCKET_NAME.s3-website-us-east-1.amazonaws.com`
- **Admin Login**: Use the credentials you set up (admin/Admin123!)

## Next Steps (Optional)

### 1. Set up Custom Domain
```bash
# If you have a domain, create Route 53 hosted zone
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Point domain to your S3 bucket
# (See full guide in AWS_DEPLOYMENT_GUIDE.md)
```

### 2. Enable SSL/HTTPS
```bash
# Request SSL certificate
aws acm request-certificate \
    --domain-name yourdomain.com \
    --validation-method DNS

# Set up CloudFront distribution
# (See full guide in AWS_DEPLOYMENT_GUIDE.md)
```

### 3. Set up Database (RDS)
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier diy-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username dbadmin \
    --master-user-password YourPassword123! \
    --allocated-storage 20

# Update your .env file to use RDS instead of SQLite
```

## 💰 Cost Estimate

- **EC2 t3.medium**: ~$30/month
- **S3 (10GB + requests)**: ~$3/month
- **Data transfer**: ~$5/month
- **Total**: ~$38/month

## 🔧 Troubleshooting

### Can't connect to API?
- Check security group allows port 8001
- Verify Docker containers are running: `docker ps`
- Check logs: `docker-compose logs backend`

### Frontend not loading?
- Verify S3 bucket policy allows public read
- Check that VITE_API_URL points to correct backend

### Database issues?
- Check SQLite file permissions
- For production, switch to RDS PostgreSQL

## 🆘 Need Help?

1. Check the full [AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md)
2. Look at the [GitHub Issues](https://github.com/yourusername/DIYList/issues)
3. Review AWS CloudWatch logs

---

**Tip**: For production use, consider using the full scalable deployment with ECS, RDS, and CloudFront from the complete guide!