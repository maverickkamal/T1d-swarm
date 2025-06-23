#!/bin/bash

# Deployment script for Google Cloud Run
set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="adk-frontend"
BACKEND_URL=${BACKEND_URL:-"https://your-backend-service-url.run.app"}

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set"
    echo "Please set PROJECT_ID: export PROJECT_ID=your-gcp-project-id"
    exit 1
fi

echo "🚀 Deploying ADK Frontend to Google Cloud Run..."
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo "   Backend URL: $BACKEND_URL"

# Build and push the Docker image
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$(date +%Y%m%d-%H%M%S)"

echo "📦 Building Docker image: $IMAGE_TAG"
docker build -t $IMAGE_TAG .

echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_TAG

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars BACKEND_URL=$BACKEND_URL \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --project $PROJECT_ID

echo "✅ Deployment complete!"
echo "🌐 Service URL:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID 