@echo off
REM Deployment script for Google Cloud Run (Windows) with .env file support
setlocal enabledelayedexpansion

echo 🔧 Loading environment variables from .env file...

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found
    echo Please create a .env file with your environment variables
    echo.
    echo Example .env file:
    echo PROJECT_ID=your-gcp-project-id
    echo BACKEND_URL=https://your-backend-service-url.run.app
    echo REGION=us-central1
    echo.
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
    echo Please add PROJECT_ID=your-gcp-project-id to your .env file
    exit /b 1
)

REM Set default backend URL if not provided
if "%BACKEND_URL%"=="" (
    echo ⚠️  Warning: BACKEND_URL not found in .env file
    set BACKEND_URL=https://your-backend-service-url.run.app
    echo Using default: %BACKEND_URL%
)

echo ✅ Environment variables loaded:
echo    PROJECT_ID: %PROJECT_ID%
echo    REGION: %REGION%
echo    SERVICE_NAME: %SERVICE_NAME%
echo    BACKEND_URL: %BACKEND_URL%
echo.

echo 🚀 Deploying ADK Frontend to Google Cloud Run...

REM Generate timestamp for image tag
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
set IMAGE_TAG=gcr.io/%PROJECT_ID%/%SERVICE_NAME%:%mydate%-%mytime%

echo 📦 Building Docker image: %IMAGE_TAG%
docker build -t %IMAGE_TAG% .
if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)

echo 📤 Pushing image to Google Container Registry...
docker push %IMAGE_TAG%
if errorlevel 1 (
    echo ❌ Docker push failed
    exit /b 1
)

echo 🚀 Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_TAG% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --port 8080 ^
    --set-env-vars BACKEND_URL=%BACKEND_URL% ^
    --memory 512Mi ^
    --cpu 1 ^
    --max-instances 10 ^
    --project %PROJECT_ID%

if errorlevel 1 (
    echo ❌ Cloud Run deployment failed
    exit /b 1
)

echo ✅ Deployment complete!
echo 🌐 Service URL:
gcloud run services describe %SERVICE_NAME% --platform managed --region %REGION% --format "value(status.url)" --project %PROJECT_ID% 