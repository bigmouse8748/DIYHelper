@echo off
REM Quick backend update for cheasydiy.com - uses existing infrastructure
setlocal EnableDelayedExpansion

echo ========================================
echo   🔄 Quick Backend Update - cheasydiy.com
echo ========================================

REM Configuration from existing deployment
set AWS_ACCOUNT_ID=571600828655
set REGION=us-east-1
set BACKEND_REPO=%AWS_ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/cheasydiy/backend

echo 📋 Current Configuration:
echo - Backend Repo: %BACKEND_REPO%
echo - API URL: https://api.cheasydiy.com

REM Get OpenAI API key
set /p OPENAI_API_KEY="Enter your OpenAI API key: "
if "%OPENAI_API_KEY%"=="" (
    echo ❌ OpenAI API key is required
    exit /b 1
)

echo 🔑 Logging into ECR...
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

echo 📦 Building and pushing updated backend...
cd diy-agent-system\backend

REM Build with timestamp tag
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

docker build -t diy-assistant-backend .
docker tag diy-assistant-backend:latest %BACKEND_REPO%:latest
docker tag diy-assistant-backend:latest %BACKEND_REPO%:%TIMESTAMP%

docker push %BACKEND_REPO%:latest
docker push %BACKEND_REPO%:%TIMESTAMP%

cd ..\..

echo 🚀 Finding and updating ECS service...

REM Auto-find ECS cluster
for /f "tokens=*" %%i in ('aws ecs list-clusters --query "clusterArns[*]" --output text') do (
    for %%j in (%%i) do (
        for /f "tokens=4 delims=/" %%k in ("%%j") do (
            echo Found cluster: %%k
            set ECS_CLUSTER=%%k
            goto :found_cluster
        )
    )
)
:found_cluster

REM Auto-find ECS service
for /f "tokens=*" %%i in ('aws ecs list-services --cluster %ECS_CLUSTER% --query "serviceArns[*]" --output text') do (
    for %%j in (%%i) do (
        for /f "tokens=4 delims=/" %%k in ("%%j") do (
            echo Found service: %%k
            set ECS_SERVICE=%%k
            goto :found_service
        )
    )
)
:found_service

echo Using ECS Cluster: %ECS_CLUSTER%
echo Using ECS Service: %ECS_SERVICE%

REM Force new deployment with latest image
echo Forcing ECS service update...
aws ecs update-service --cluster %ECS_CLUSTER% --service %ECS_SERVICE% --force-new-deployment

echo ⏳ Waiting for deployment to complete...
aws ecs wait services-stable --cluster %ECS_CLUSTER% --services %ECS_SERVICE%

echo 🧪 Testing updated API...
timeout /t 15 /nobreak > nul
curl -f https://api.cheasydiy.com/api/test && (
    echo ✅ Backend update successful!
    echo 🎉 DIY Smart Assistant backend is updated and running!
) || (
    echo ❌ API test failed, check ECS logs
)

echo.
echo 📊 Check deployment status:
echo - ECS Console: https://console.aws.amazon.com/ecs/
echo - CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/
echo - API Health: https://api.cheasydiy.com/api/test

endlocal
pause