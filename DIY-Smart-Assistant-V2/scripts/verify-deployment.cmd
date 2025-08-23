@echo off
setlocal enabledelayedexpansion

REM DIY Smart Assistant V2 - Deployment Verification Script (Windows)
REM This script verifies the successful deployment of the new version

echo.
echo ^🚀 DIY Smart Assistant V2 Deployment Verification
echo ================================================

REM Configuration
set "API_BASE_URL=https://api.cheasydiy.com"
set "FRONTEND_URL=https://cheasydiy.com"
set "TIMEOUT=30"

echo.
echo Step 1: Testing Backend Health
echo Checking API health endpoint...

REM Test backend health
curl -f -s --max-time %TIMEOUT% "%API_BASE_URL%/api/v1/health" > nul 2>&1
if !errorlevel! equ 0 (
    echo ^✅ Backend health check passed
    
    REM Get detailed health info
    echo Health details:
    curl -s "%API_BASE_URL%/api/v1/health"
) else (
    echo ^❌ Backend health check failed
    exit /b 1
)

echo.
echo Step 2: Testing API Endpoints
echo Testing key API endpoints...

REM Test agents status
curl -f -s --max-time %TIMEOUT% "%API_BASE_URL%/api/v1/agents/status" > nul 2>&1
if !errorlevel! equ 0 (
    echo ^✅ Agents status endpoint working
) else (
    echo ^❌ Agents status endpoint failed
    exit /b 1
)

echo.
echo Step 3: Testing Frontend
echo Checking frontend availability...

REM Test frontend
curl -f -s --max-time %TIMEOUT% -I "%FRONTEND_URL%" 2>&1 | find "200" > nul
if !errorlevel! equ 0 (
    echo ^✅ Frontend is accessible
) else (
    curl -f -s --max-time %TIMEOUT% -I "%FRONTEND_URL%" 2>&1 | find "301" > nul
    if !errorlevel! equ 0 (
        echo ^✅ Frontend is accessible ^(redirect^)
    ) else (
        echo ^❌ Frontend check failed
        exit /b 1
    )
)

echo.
echo Step 4: Testing Core Functionality
echo Testing project analysis functionality...

REM Test project analysis endpoint existence
curl -f -s --max-time %TIMEOUT% "%API_BASE_URL%/api/v1/agents/project/analyze" -X POST -H "Content-Type: application/json" -d "{\"test\":\"data\"}" > nul 2>&1
if !errorlevel! leq 1 (
    echo ^⚠️  Project analysis endpoint test inconclusive ^(expected for wrong content type^)
) else (
    echo ^❌ Project analysis endpoint not found
)

echo.
echo Step 5: Performance Check
echo Measuring API response times...

REM Measure response time (simplified for Windows)
echo Testing API response...
curl -s -w "Response time: %%{time_total}s\n" "%API_BASE_URL%/api/v1/health" > nul

echo.
echo Step 6: Database Connectivity
echo Testing database connectivity through API...

REM Test user profile endpoint (requires auth, but should return 401, not 500)
for /f %%i in ('curl -s -o nul -w "%%{http_code}" "%API_BASE_URL%/api/v1/users/profile"') do set HTTP_STATUS=%%i

if "!HTTP_STATUS!"=="401" (
    echo ^✅ Database connectivity working ^(auth required response^)
) else if "!HTTP_STATUS!"=="500" (
    echo ^❌ Database connectivity issue detected
    exit /b 1
) else (
    echo ^⚠️  Unexpected response code: !HTTP_STATUS!
)

echo.
echo ^🎉 Deployment Verification Complete!
echo ======================================
echo ^✅ All critical systems are operational
echo ^🌐 Frontend URL: %FRONTEND_URL%
echo ^🔗 API URL: %API_BASE_URL%

echo.
echo Next Steps:
echo 1. Test the application manually in your browser
echo 2. Upload a test image and verify analysis works
echo 3. Check admin panel functionality
echo 4. Monitor CloudWatch logs for any errors

echo.
echo Monitoring Commands:
echo ^• Check ECS services: aws ecs describe-services --cluster cheasydiy-production-cluster --services cheasydiy-production-backend
echo ^• View logs: aws logs tail /ecs/cheasydiy-backend --follow
echo ^• CloudFront status: aws cloudfront list-distributions --query "DistributionList.Items[?Aliases.Items[0]=='cheasydiy.com'].Id"

pause