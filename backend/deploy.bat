@echo off
REM T1D-Swarm Cloud Run Deployment Script for Windows
REM Runs from backend/ directory and reads configuration from parent .env file

setlocal enabledelayedexpansion

echo.
echo 🚀 T1D-Swarm Cloud Run Deployment
echo.

REM Check if .env file exists in parent directory
if not exist "../.env" (
    echo ❌ .env file not found in parent directory. Please create one with your configuration.
    echo Expected location: ../.env (relative to backend folder)
    exit /b 1
)

echo 📋 Loading environment variables from ../.env
REM Load environment variables from parent .env file
for /f "usebackq tokens=1,2 delims==" %%a in ("../.env") do (
    set "line=%%a"
    if not "!line:~0,1!"=="#" if not "!line!"=="" (
        set "%%a=%%b"
    )
)

REM Set defaults and validate
set PROJECT_ID=%1
if "%PROJECT_ID%"=="" set PROJECT_ID=%GOOGLE_CLOUD_PROJECT%

set REGION=%2
if "%REGION%"=="" set REGION=%GOOGLE_CLOUD_LOCATION%
if "%REGION%"=="" set REGION=us-central1

if "%PROJECT_ID%"=="" (
    echo ❌ PROJECT_ID not found. Set GOOGLE_CLOUD_PROJECT in ../.env or pass as argument
    echo Usage: deploy.bat PROJECT_ID [REGION]
    exit /b 1
)


echo Project ID: %PROJECT_ID%
echo Region: %REGION%
echo Running from: backend\ directory
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ gcloud CLI is not installed or not in PATH
    echo Please install it from: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

REM Set the project
echo 📋 Setting project to %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

REM Build the Docker image from current directory (backend)
echo 🔨 Building Docker image from backend directory
gcloud builds submit --tag gcr.io/%PROJECT_ID%/t1d-swarm .

if %errorlevel% neq 0 (
    echo ❌ Build failed!
    exit /b 1
)

REM Deploy to Cloud Run with environment variables from .env
echo 🚀 Deploying to Cloud Run with environment from ../.env
gcloud run deploy t1d-swarm ^
    --image gcr.io/%PROJECT_ID%/t1d-swarm ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 2Gi ^
    --cpu 2 ^
    --max-instances 10 ^
    --port 8080 ^
    --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%" ^
    --set-env-vars "GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --set-env-vars "GOOGLE_CLOUD_LOCATION=%REGION%" ^
    --set-env-vars "GENERATE_SCENARIO_MODEL=%GENERATE_SCENARIO_MODEL%" ^
    --set-env-vars "AMBIENT_CONTEXT_MODEL=%AMBIENT_CONTEXT_MODEL%" ^
    --set-env-vars "SIMULATED_CGM_MODEL=%SIMULATED_CGM_MODEL%" ^
    --set-env-vars "GLYCEMIC_FORECAST_MODEL=%GLYCEMIC_FORECAST_MODEL%" ^
    --set-env-vars "FORECAST_VERIFIER_MODEL=%FORECAST_VERIFIER_MODEL%" ^
    --set-env-vars "INSIGHT_PRESENTER_MODEL=%INSIGHT_PRESENTER_MODEL%" ^
    --set-env-vars "ENVIRONMENT=production"

if %errorlevel% neq 0 (
    echo ❌ Deployment failed!
    exit /b 1
)

REM Get the service URL
for /f "tokens=*" %%i in ('gcloud run services describe t1d-swarm --platform managed --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ✅ Deployment completed successfully!
echo 🌐 Your service is available at: %SERVICE_URL%
echo 📖 API Documentation: %SERVICE_URL%/docs
echo ❤️  Health Check: %SERVICE_URL%/current-session
echo 🔑 Test Authentication: %SERVICE_URL%/api/check-access
echo.
echo 🔐 Environment Variables Deployed:
echo • Project: %PROJECT_ID%
echo • Region: %REGION%
echo • AI Models: %GENERATE_SCENARIO_MODEL%, %AMBIENT_CONTEXT_MODEL%, etc.
echo.

set /p SHOW_LOGS="Do you want to view the logs? (y/n): "
if /i "%SHOW_LOGS%"=="y" (
    echo 📋 Showing recent logs
    gcloud run services logs tail t1d-swarm --region %REGION%
)

echo.
echo 💡 To update environment variables, modify ../.env and redeploy 