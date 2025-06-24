# PowerShell deployment script for Google Cloud Run with .env file support

Write-Host "🔧 Loading environment variables from .env file..." -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    Write-Host "Please create a .env file with your environment variables" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Example .env file:" -ForegroundColor Yellow
    Write-Host "PROJECT_ID=your-gcp-project-id"
    Write-Host "BACKEND_URL=https://your-backend-service-url.run.app"
    Write-Host "REGION=us-central1"
    Write-Host ""
    exit 1
}

# Load environment variables from .env file
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]*)\s*=\s*(.*)\s*$") {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Variable -Name $name -Value $value -Scope Global
        Write-Host "Set $name=$value" -ForegroundColor Gray
    }
}

# Configuration
$SERVICE_NAME = "adk-frontend"
if (-not $REGION) { $REGION = "us-central1" }

# Check if PROJECT_ID is set
if (-not $PROJECT_ID) {
    Write-Host "❌ Error: PROJECT_ID not found in .env file" -ForegroundColor Red
    Write-Host "Please add PROJECT_ID=your-gcp-project-id to your .env file" -ForegroundColor Yellow
    exit 1
}

# Set default backend URL if not provided
if (-not $BACKEND_URL) {
    Write-Host "⚠️  Warning: BACKEND_URL not found in .env file" -ForegroundColor Yellow
    $BACKEND_URL = "https://your-backend-service-url.run.app"
    Write-Host "Using default: $BACKEND_URL" -ForegroundColor Yellow
}

Write-Host "✅ Environment variables loaded:" -ForegroundColor Green
Write-Host "   PROJECT_ID: $PROJECT_ID"
Write-Host "   REGION: $REGION" 
Write-Host "   SERVICE_NAME: $SERVICE_NAME"
Write-Host "   BACKEND_URL: $BACKEND_URL"
Write-Host ""

Write-Host "🚀 Deploying ADK Frontend to Google Cloud Run..." -ForegroundColor Cyan

# Generate timestamp for image tag
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$timestamp"

Write-Host "📦 Building Docker image: $IMAGE_TAG" -ForegroundColor Yellow
docker build -t $IMAGE_TAG .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "📤 Pushing image to Google Container Registry..." -ForegroundColor Yellow
docker push $IMAGE_TAG
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars "BACKEND_URL=$BACKEND_URL" `
    --memory 512Mi `
    --cpu 1 `
    --max-instances 10 `
    --project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cloud Run deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Service URL:" -ForegroundColor Cyan
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)" --project $PROJECT_ID 