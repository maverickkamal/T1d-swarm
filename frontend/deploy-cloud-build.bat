@echo off
REM Deployment script using Cloud Build (no local Docker required)
setlocal enabledelayedexpansion

echo 🔧 Loading environment variables from .env file...

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found
    echo Please create a .env file with your environment variables
    exit /b 1
)

REM Load environment variables from .env file
for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
    REM Skip empty lines and comments
    if not "%%a"=="" (
        if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Configuration
set SERVICE_NAME=adk-frontend
if "%REGION%"=="" set REGION=us-central1

REM Check if PROJECT_ID is set
if "%PROJECT_ID%"=="" (
    echo ❌ Error: PROJECT_ID not found in .env file
    exit /b 1
)

if "%BACKEND_URL%"=="" (
    echo ⚠️  Warning: BACKEND_URL not found in .env file
    set BACKEND_URL=https://your-backend-service-url.run.app
)

echo ✅ Environment variables loaded:
echo    PROJECT_ID: %PROJECT_ID%
echo    REGION: %REGION%
echo    SERVICE_NAME: %SERVICE_NAME%
echo    BACKEND_URL: %BACKEND_URL%
echo.

echo 🚀 Deploying ADK Frontend using Cloud Build...
echo 📤 Submitting build to Google Cloud Build...

REM Use Cloud Build to build and deploy
gcloud builds submit --config cloudbuild.yaml ^
    --substitutions _BACKEND_URL=%BACKEND_URL% ^
    --project %PROJECT_ID%

if errorlevel 1 (
    echo ❌ Cloud Build deployment failed
    exit /b 1
)

echo ✅ Cloud Build deployment complete!
echo 🌐 Service URL:
gcloud run services describe %SERVICE_NAME% --platform managed --region %REGION% --format "value(status.url)" --project %PROJECT_ID% 