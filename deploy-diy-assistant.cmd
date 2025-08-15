@echo off
REM DIY Smart Assistant - Deploy to cheasydiy.com Infrastructure
REM This script follows the existing deployment patterns from WINDOWS_COMMANDS_SUMMARY.md

setlocal EnableDelayedExpansion

echo =======================================================
echo   🚀 Deploying DIY Smart Assistant to cheasydiy.com
echo =======================================================

REM Configuration from existing infrastructure
set AWS_ACCOUNT_ID=571600828655
set REGION=us-east-1
set BACKEND_REPO=%AWS_ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/cheasydiy/backend
set FRONTEND_REPO=%AWS_ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/cheasydiy/frontend

REM Get OpenAI API key
set /p OPENAI_API_KEY="Enter your OpenAI API key: "
if "%OPENAI_API_KEY%"=="" (
    echo ❌ OpenAI API key is required
    exit /b 1
)

REM Generate JWT secret
for /f "delims=" %%i in ('openssl rand -hex 32') do set JWT_SECRET=%%i

echo 📋 Configuration:
echo - AWS Account: %AWS_ACCOUNT_ID%
echo - Region: %REGION%
echo - Backend Repo: %BACKEND_REPO%
echo - Frontend Repo: %FRONTEND_REPO%
echo - API URL: https://api.cheasydiy.com
echo - Frontend URL: https://cheasydiy.com

pause

echo 🔑 Logging into ECR...
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com
if errorlevel 1 (
    echo ❌ ECR login failed
    exit /b 1
)

echo 📦 Building and pushing backend...
cd diy-agent-system\backend

REM Create production Dockerfile if needed
if not exist "Dockerfile.prod" (
    echo Creating production Dockerfile...
    copy Dockerfile Dockerfile.prod
)

REM Build backend with production config
docker build -t diy-assistant-backend .
docker tag diy-assistant-backend:latest %BACKEND_REPO%:latest
docker tag diy-assistant-backend:latest %BACKEND_REPO%:v1.0.0

REM Push backend images
echo Pushing backend images...
docker push %BACKEND_REPO%:latest
docker push %BACKEND_REPO%:v1.0.0

cd ..\..

echo 🌐 Building and pushing frontend...
cd diy-agent-system\frontend

REM Set API URL for production build
set VITE_API_URL=https://api.cheasydiy.com

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

REM Build frontend
echo Building frontend for production...
npm run build

REM Check if we need to build Docker image or deploy directly to S3
echo.
echo Choose deployment method for frontend:
echo 1. Direct S3 deployment (faster, recommended)
echo 2. Docker image to ECR (for ECS deployment)
set /p FRONTEND_METHOD="Select option (1 or 2): "

if "%FRONTEND_METHOD%"=="2" (
    REM Build frontend Docker image
    docker build --build-arg VITE_API_URL=https://api.cheasydiy.com -t diy-assistant-frontend .
    docker tag diy-assistant-frontend:latest %FRONTEND_REPO%:latest
    docker tag diy-assistant-frontend:latest %FRONTEND_REPO%:v1.0.0
    
    echo Pushing frontend images...
    docker push %FRONTEND_REPO%:latest
    docker push %FRONTEND_REPO%:v1.0.0
) else (
    REM Direct S3 deployment
    echo Getting S3 bucket from Terraform...
    cd ..\..\terraform
    if exist "terraform.tfstate" (
        terraform output -raw frontend_s3_bucket > s3_bucket.txt
        terraform output -raw cloudfront_distribution_id > cloudfront_id.txt
        set /p S3_BUCKET=<s3_bucket.txt
        set /p CLOUDFRONT_ID=<cloudfront_id.txt
        del s3_bucket.txt cloudfront_id.txt
    ) else (
        REM Fallback - find S3 bucket manually
        echo Terraform state not found, finding S3 bucket...
        for /f "tokens=*" %%i in ('aws s3 ls ^| findstr cheasydiy') do set S3_BUCKET_LINE=%%i
        for %%j in (%S3_BUCKET_LINE%) do set S3_BUCKET=%%j
        
        echo Finding CloudFront distribution...
        for /f "tokens=*" %%i in ('aws cloudfront list-distributions --query "DistributionList.Items[?contains(Comment, 'cheasydiy') || contains(Origins.Items[0].DomainName, 'cheasydiy')].Id" --output text') do set CLOUDFRONT_ID=%%i
    )
    
    if "%S3_BUCKET%"=="" (
        set /p S3_BUCKET="Enter S3 bucket name for frontend: "
    )
    
    echo Deploying to S3 bucket: %S3_BUCKET%
    cd ..\diy-agent-system\frontend
    
    REM Deploy to S3 with caching strategy
    aws s3 sync dist/ s3://%S3_BUCKET% --delete --cache-control "public, max-age=31536000" --exclude "index.html" --exclude "*.json"
    aws s3 cp dist/index.html s3://%S3_BUCKET%/index.html --cache-control "no-cache, no-store, must-revalidate"
    aws s3 cp dist/ s3://%S3_BUCKET%/ --recursive --exclude "*" --include "*.json" --cache-control "no-cache, no-store, must-revalidate"
    
    REM Invalidate CloudFront
    if not "%CLOUDFRONT_ID%"=="" (
        echo Invalidating CloudFront cache...
        aws cloudfront create-invalidation --distribution-id %CLOUDFRONT_ID% --paths "/*"
    )
)

cd ..\..

echo 🚀 Updating ECS backend service...

REM Find ECS cluster and service
echo Finding ECS resources...
for /f "tokens=*" %%i in ('aws ecs list-clusters --query "clusterArns[*]" --output text') do (
    for %%j in (%%i) do (
        for /f "tokens=4 delims=/" %%k in ("%%j") do set ECS_CLUSTER=%%k
    )
)

if "%ECS_CLUSTER%"=="" (
    set /p ECS_CLUSTER="Enter ECS cluster name: "
)

REM Find service in cluster
for /f "tokens=*" %%i in ('aws ecs list-services --cluster %ECS_CLUSTER% --query "serviceArns[*]" --output text') do (
    for %%j in (%%i) do (
        for /f "tokens=4 delims=/" %%k in ("%%j") do set ECS_SERVICE=%%k
    )
)

if "%ECS_SERVICE%"=="" (
    set ECS_SERVICE=cheasydiy-production-backend
    echo Using default service name: %ECS_SERVICE%
)

echo Cluster: %ECS_CLUSTER%
echo Service: %ECS_SERVICE%

REM Create task definition
echo Creating ECS task definition...
(
echo {
echo   "family": "diy-assistant-backend",
echo   "networkMode": "awsvpc",
echo   "requiresCompatibilities": ["FARGATE"],
echo   "cpu": "512",
echo   "memory": "1024",
echo   "executionRoleArn": "arn:aws:iam::%AWS_ACCOUNT_ID%:role/ecsTaskExecutionRole",
echo   "containerDefinitions": [
echo     {
echo       "name": "backend",
echo       "image": "%BACKEND_REPO%:latest",
echo       "portMappings": [
echo         {
echo           "containerPort": 8001,
echo           "protocol": "tcp"
echo         }
echo       ],
echo       "environment": [
echo         {"name": "OPENAI_API_KEY", "value": "%OPENAI_API_KEY%"},
echo         {"name": "JWT_SECRET_KEY", "value": "%JWT_SECRET%"},
echo         {"name": "ADMIN_SETUP_KEY", "value": "setup_admin_cheasydiy_2025"},
echo         {"name": "AWS_REGION", "value": "%REGION%"},
echo         {"name": "CORS_ORIGINS", "value": "https://cheasydiy.com,https://www.cheasydiy.com"},
echo         {"name": "ENVIRONMENT", "value": "production"}
echo       ],
echo       "logConfiguration": {
echo         "logDriver": "awslogs",
echo         "options": {
echo           "awslogs-group": "/ecs/diy-assistant",
echo           "awslogs-region": "%REGION%",
echo           "awslogs-stream-prefix": "backend",
echo           "awslogs-create-group": "true"
echo         }
echo       },
echo       "healthCheck": {
echo         "command": ["CMD-SHELL", "curl -f http://localhost:8001/api/test || exit 1"],
echo         "interval": 30,
echo         "timeout": 5,
echo         "retries": 3
echo       }
echo     }
echo   ]
echo }
) > task-definition.json

REM Register task definition
echo Registering task definition...
for /f "tokens=*" %%i in ('aws ecs register-task-definition --cli-input-json file://task-definition.json --query "taskDefinition.taskDefinitionArn" --output text') do set TASK_DEF_ARN=%%i

REM Update ECS service
echo Updating ECS service with new task definition...
aws ecs update-service --cluster %ECS_CLUSTER% --service %ECS_SERVICE% --task-definition %TASK_DEF_ARN% --force-new-deployment

REM Clean up
del task-definition.json

echo ⏳ Waiting for ECS service to stabilize...
aws ecs wait services-stable --cluster %ECS_CLUSTER% --services %ECS_SERVICE%

echo 🎉 Deployment completed successfully!
echo =======================================
echo.
echo 🌐 Frontend: https://cheasydiy.com
echo 🔌 Backend API: https://api.cheasydiy.com
echo 🏥 Health Check: https://api.cheasydiy.com/api/test
echo 👤 Admin Panel: https://cheasydiy.com/admin
echo.
echo 🔑 Admin Credentials:
echo - Username: admin
echo - Password: Admin123!
echo.
echo 📝 Next Steps:
echo 1. Test the application: https://cheasydiy.com
echo 2. Check API health: https://api.cheasydiy.com/api/test
echo 3. Login to admin panel: https://cheasydiy.com/admin
echo 4. Add product URLs to test AI extraction
echo.

REM Test endpoints
echo 🧪 Testing endpoints...
timeout /t 30 /nobreak > nul
curl -f https://api.cheasydiy.com/api/test && echo ✅ API is working! || echo ❌ API test failed
curl -I https://cheasydiy.com && echo ✅ Frontend is working! || echo ❌ Frontend test failed

echo.
echo ✅ DIY Smart Assistant is now live at https://cheasydiy.com!

endlocal
pause