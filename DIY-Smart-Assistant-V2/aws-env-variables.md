# AWS ECS Environment Variables Configuration

## Backend Environment Variables (ECS Task Definition)

These environment variables should be configured in your ECS task definition or through AWS Systems Manager Parameter Store:

```json
{
  "environment": [
    {
      "name": "APP_NAME",
      "value": "DIY Smart Assistant"
    },
    {
      "name": "APP_VERSION",
      "value": "2.0.0"
    },
    {
      "name": "DEBUG",
      "value": "false"
    },
    {
      "name": "PORT",
      "value": "8000"
    },
    {
      "name": "HOST",
      "value": "0.0.0.0"
    },
    {
      "name": "BASE_URL",
      "value": "https://api.cheasydiy.com"
    },
    {
      "name": "DATABASE_URL",
      "value": "postgresql://username:password@rds-endpoint:5432/diyassistant"
    },
    {
      "name": "ALLOWED_ORIGINS",
      "value": "https://cheasydiy.com,https://www.cheasydiy.com"
    },
    {
      "name": "ACCESS_TOKEN_EXPIRE_MINUTES",
      "value": "30"
    },
    {
      "name": "REFRESH_TOKEN_EXPIRE_DAYS",
      "value": "7"
    },
    {
      "name": "ALGORITHM",
      "value": "HS256"
    },
    {
      "name": "MAX_FILE_SIZE_MB",
      "value": "10"
    },
    {
      "name": "ALLOWED_FILE_TYPES",
      "value": "jpg,jpeg,png,webp"
    },
    {
      "name": "UPLOAD_PATH",
      "value": "/app/uploads/"
    }
  ],
  "secrets": [
    {
      "name": "SECRET_KEY",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:account-id:secret:diy-assistant/secret-key"
    },
    {
      "name": "OPENAI_API_KEY",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:account-id:secret:diy-assistant/openai-api-key"
    },
    {
      "name": "REDIS_URL",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:account-id:secret:diy-assistant/redis-url"
    },
    {
      "name": "SENTRY_DSN",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:account-id:secret:diy-assistant/sentry-dsn"
    }
  ]
}
```

## Frontend Build Arguments (Docker/GitHub Actions)

For frontend builds during CI/CD:

```bash
# In GitHub Actions workflow
docker build --build-arg VITE_API_URL=https://api.cheasydiy.com -t frontend .
```

## AWS Secrets Manager Setup

Create the following secrets in AWS Secrets Manager:

```bash
# Create secret key
aws secretsmanager create-secret \
  --name diy-assistant/secret-key \
  --secret-string "$(openssl rand -hex 32)"

# Create OpenAI API key secret
aws secretsmanager create-secret \
  --name diy-assistant/openai-api-key \
  --secret-string "your-openai-api-key"

# Create Redis URL secret (if using ElastiCache)
aws secretsmanager create-secret \
  --name diy-assistant/redis-url \
  --secret-string "redis://your-elasticache-endpoint:6379"

# Create Sentry DSN secret (if using Sentry)
aws secretsmanager create-secret \
  --name diy-assistant/sentry-dsn \
  --secret-string "your-sentry-dsn"
```

## GitHub Actions Secrets

Configure these secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`: AWS access key for deployment
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `VITE_API_URL`: https://api.cheasydiy.com
- `S3_BUCKET_NAME`: cheasydiy.com (for frontend deployment)
- `CLOUDFRONT_DISTRIBUTION_ID`: Your CloudFront distribution ID