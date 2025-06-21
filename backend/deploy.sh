#!/bin/bash

# T1D-Swarm Cloud Run Deployment Script
# Runs from backend/ directory and reads configuration from parent .env file

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables from parent .env file
if [ -f "../.env" ]; then
    echo -e "${BLUE}📋 Loading environment variables from ../.env${NC}"
    # Export variables from .env file
    export $(grep -v '^#' ../.env | grep -v '^$' | xargs)
else
    echo -e "${RED}❌ .env file not found in parent directory. Please create one with your configuration.${NC}"
    echo -e "${YELLOW}Expected location: ../.env (relative to backend folder)${NC}"
    exit 1
fi

# Configuration
PROJECT_ID=${1:-$GOOGLE_CLOUD_PROJECT}
REGION=${2:-$GOOGLE_CLOUD_LOCATION}
SERVICE_NAME="t1d-swarm"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Validate required variables
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ PROJECT_ID not found. Set GOOGLE_CLOUD_PROJECT in ../.env or pass as argument${NC}"
    exit 1
fi

if [ -z "$JUDGE_CODES" ]; then
    echo -e "${RED}❌ JUDGE_CODES not found in ../.env file${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Starting T1D-Swarm deployment to Cloud Run${NC}"
echo -e "${YELLOW}Project ID: $PROJECT_ID${NC}"
echo -e "${YELLOW}Region: $REGION${NC}"
echo -e "${YELLOW}Service Name: $SERVICE_NAME${NC}"
echo -e "${YELLOW}Running from: backend/ directory${NC}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not authenticated with gcloud. Please run 'gcloud auth login'${NC}"
    exit 1
fi

# Set the project
echo -e "${BLUE}📋 Setting project to $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${BLUE}🔧 Enabling required APIs${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image from current directory (backend)
echo -e "${BLUE}🔨 Building Docker image from backend directory${NC}"
gcloud builds submit --tag $IMAGE_NAME .

# Deploy to Cloud Run with environment variables from .env
echo -e "${BLUE}🚀 Deploying to Cloud Run with environment from ../.env${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --port 8080 \
    --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI:-true}" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "GOOGLE_CLOUD_LOCATION=$REGION" \
    --set-env-vars "GENERATE_SCENARIO_MODEL=${GENERATE_SCENARIO_MODEL}" \
    --set-env-vars "AMBIENT_CONTEXT_MODEL=${AMBIENT_CONTEXT_MODEL}" \
    --set-env-vars "SIMULATED_CGM_MODEL=${SIMULATED_CGM_MODEL}" \
    --set-env-vars "GLYCEMIC_FORECAST_MODEL=${GLYCEMIC_FORECAST_MODEL}" \
    --set-env-vars "FORECAST_VERIFIER_MODEL=${FORECAST_VERIFIER_MODEL}" \
    --set-env-vars "INSIGHT_PRESENTER_MODEL=${INSIGHT_PRESENTER_MODEL}" \
    --set-env-vars "JUDGE_CODES=$JUDGE_CODES" \
    --set-env-vars "ENVIRONMENT=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your service is available at: $SERVICE_URL${NC}"
echo -e "${YELLOW}📖 API Documentation: $SERVICE_URL/docs${NC}"
echo -e "${YELLOW}❤️  Health Check: $SERVICE_URL/current-session${NC}"
echo -e "${YELLOW}🔑 Test Authentication: $SERVICE_URL/api/check-access${NC}"
echo
echo -e "${BLUE}🔐 Environment Variables Deployed:${NC}"
echo -e "${YELLOW}• Project: $PROJECT_ID${NC}"
echo -e "${YELLOW}• Region: $REGION${NC}"
echo -e "${YELLOW}• Judge Codes: [HIDDEN FOR SECURITY]${NC}"
echo -e "${YELLOW}• AI Models: ${GENERATE_SCENARIO_MODEL}, ${AMBIENT_CONTEXT_MODEL}, etc.${NC}"

# Optional: Show logs
read -p "Do you want to view the logs? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}📋 Showing recent logs${NC}"
    gcloud run services logs tail $SERVICE_NAME --region $REGION
fi 