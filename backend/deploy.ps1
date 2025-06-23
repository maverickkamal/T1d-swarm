# T1D-Swarm Cloud Run Deployment Script for Windows PowerShell
# Runs from backend/ directory and reads configuration from parent .env file

Write-Host ""
Write-Host "🚀 T1D-Swarm Cloud Run Deployment" -ForegroundColor Blue
Write-Host ""

# Check if .env file exists in parent directory
if (-not (Test-Path "../.env")) {
    Write-Host "❌ .env file not found in parent directory. Please create one with your configuration." -ForegroundColor Red
    Write-Host "Expected location: ../.env (relative to backend folder)" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Loading environment variables from ../.env" -ForegroundColor Blue

# Load environment variables from parent .env file
$envVars = @{}
Get-Content "../.env" | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$name] = $value
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Set defaults and validate
$PROJECT_ID = if ($args[0]) { $args[0] } else { $envVars["GOOGLE_CLOUD_PROJECT"] }
$REGION = if ($args[1]) { $args[1] } else { $envVars["GOOGLE_CLOUD_LOCATION"] }
if (-not $REGION) { $REGION = "us-central1" }

if (-not $PROJECT_ID) {
    Write-Host "❌ PROJECT_ID not found. Set GOOGLE_CLOUD_PROJECT in ../.env or pass as argument" -ForegroundColor Red
    Write-Host "Usage: .\deploy.ps1 PROJECT_ID [REGION]" -ForegroundColor Yellow
    exit 1
}

Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Running from: backend\ directory" -ForegroundColor Yellow
Write-Host ""

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "❌ gcloud CLI is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Set the project
Write-Host "📋 Setting project to $PROJECT_ID" -ForegroundColor Blue
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "🔧 Enabling required APIs" -ForegroundColor Blue
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image from current directory (backend)
Write-Host "🔨 Building Docker image from backend directory" -ForegroundColor Blue
gcloud builds submit --tag "gcr.io/$PROJECT_ID/t1d-swarm" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Deploy to Cloud Run with environment variables from .env
Write-Host "🚀 Deploying to Cloud Run with environment from ../.env" -ForegroundColor Blue

$deployArgs = @(
    "run", "deploy", "t1d-swarm",
    "--image=gcr.io/$PROJECT_ID/t1d-swarm",
    "--platform=managed",
    "--region=$REGION",
    "--allow-unauthenticated",
    "--memory=2Gi",
    "--cpu=2",
    "--max-instances=5",
    "--port=8080",
    "--set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=$($envVars['GOOGLE_GENAI_USE_VERTEXAI'])",
    "--set-env-vars=GOOGLE_CLOUD_PROJECT=$PROJECT_ID",
    "--set-env-vars=GOOGLE_CLOUD_LOCATION=$REGION",
    "--set-env-vars=GENERATE_SCENARIO_MODEL=$($envVars['GENERATE_SCENARIO_MODEL'])",
    "--set-env-vars=AMBIENT_CONTEXT_MODEL=$($envVars['AMBIENT_CONTEXT_MODEL'])",
    "--set-env-vars=SIMULATED_CGM_MODEL=$($envVars['SIMULATED_CGM_MODEL'])",
    "--set-env-vars=GLYCEMIC_FORECAST_MODEL=$($envVars['GLYCEMIC_FORECAST_MODEL'])",
    "--set-env-vars=FORECAST_VERIFIER_MODEL=$($envVars['FORECAST_VERIFIER_MODEL'])",
    "--set-env-vars=INSIGHT_PRESENTER_MODEL=$($envVars['INSIGHT_PRESENTER_MODEL'])",
    "--set-env-vars=ENVIRONMENT=production"
)

& gcloud @deployArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

# Get the service URL
$SERVICE_URL = gcloud run services describe t1d-swarm --platform managed --region $REGION --format "value(status.url)"

Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Your service is available at: $SERVICE_URL" -ForegroundColor Green
Write-Host "📖 API Documentation: $SERVICE_URL/docs" -ForegroundColor Yellow
Write-Host "❤️  Health Check: $SERVICE_URL/current-session" -ForegroundColor Yellow
Write-Host "🔑 Test Authentication: $SERVICE_URL/api/check-access" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔐 Environment Variables Deployed:" -ForegroundColor Blue
Write-Host "• Project: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "• Region: $REGION" -ForegroundColor Yellow
Write-Host "• AI Models: $($envVars['GENERATE_SCENARIO_MODEL']), $($envVars['AMBIENT_CONTEXT_MODEL']), etc." -ForegroundColor Yellow
Write-Host ""

$showLogs = Read-Host "Do you want to view the logs? (y/n)"
if ($showLogs -eq "y" -or $showLogs -eq "Y") {
    Write-Host "📋 Showing recent logs" -ForegroundColor Blue
    gcloud run services logs tail t1d-swarm --region $REGION
}

Write-Host ""
Write-Host "💡 To update environment variables, modify ../.env and redeploy" -ForegroundColor Cyan 