# ADK Frontend - Google Cloud Run Deployment Guide

This guide explains how to deploy the ADK Frontend to Google Cloud Run with environment-based configuration.

## 🏗️ Architecture

The application is containerized using a multi-stage Docker build:
1. **Build Stage**: Uses Node.js to build the Angular application
2. **Runtime Stage**: Uses Nginx to serve the static files
3. **Environment Injection**: Runtime configuration is injected from environment variables

## 📋 Prerequisites

1. **Google Cloud SDK** installed and configured
2. **Docker** installed
3. **GCP Project** with the following APIs enabled:
   - Cloud Run API
   - Container Registry API (or Artifact Registry API)
   - Cloud Build API (optional, for automated builds)

## 🚀 Deployment Options

### Option 1: Quick Deploy (Recommended)

```bash
# Set your project ID and backend URL
export PROJECT_ID="your-gcp-project-id"
export BACKEND_URL="https://your-backend-service-url.run.app"

# Run the deployment script
chmod +x deploy.sh  # Linux/Mac only
./deploy.sh
```

### Option 2: Manual Deploy

```bash
# 1. Build the Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/adk-frontend .

# 2. Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/adk-frontend

# 3. Deploy to Cloud Run
gcloud run deploy adk-frontend \
    --image gcr.io/YOUR_PROJECT_ID/adk-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars BACKEND_URL=https://your-backend-url.run.app \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10
```

### Option 3: Cloud Build (CI/CD)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml \
    --substitutions _BACKEND_URL=https://your-backend-url.run.app
```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BACKEND_URL` | Backend API URL | `""` | Yes |

### Runtime Configuration

The application generates a `runtime-config.json` file at startup with the environment variables:

```json
{
  "backendUrl": "https://your-backend-service-url.run.app"
}
```

## 🏃‍♂️ Local Testing with Docker

```bash
# Build the image
npm run docker:build

# Run locally with environment variables
npm run docker:run

# Or manually:
docker run -p 8080:8080 -e BACKEND_URL=http://localhost:8000 adk-frontend
```

Access the application at `http://localhost:8080`

## 📝 NPM Scripts

The following scripts are available for Cloud Run deployment:

```bash
# Build production version
npm run build:prod

# Build Docker image
npm run docker:build

# Run Docker container locally
npm run docker:run

# Deploy to Cloud Run (uses deploy.sh)
npm run cloud:deploy

# Build with Cloud Build
npm run cloud:build
```

## 🔍 Health Checks

The application includes a health check endpoint at `/health` that returns:
- Status: `200 OK`
- Body: `healthy`

This is used by Cloud Run for:
- Liveness probes
- Readiness probes
- Load balancer health checks

## 🛡️ Security Features

1. **NGINX Security Headers**:
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - Referrer-Policy: no-referrer-when-downgrade
   - Content-Security-Policy configured

2. **Static Asset Caching**: 1 year cache for static assets

3. **Gzip Compression**: Enabled for all text-based assets

## 🎯 Performance Optimizations

1. **Multi-stage Docker build** reduces image size
2. **Nginx optimizations** for serving static files
3. **Gzip compression** reduces bandwidth
4. **Asset caching** improves load times
5. **Cloud Run autoscaling** handles traffic spikes

## 🔧 Customization

### Modify Docker Configuration

Edit `Dockerfile` to change:
- Node.js version
- Build optimizations
- Nginx configuration

### Modify Cloud Run Configuration

Edit `cloud-run-service.yaml` to change:
- Resource limits
- Scaling parameters
- Environment variables
- Health check settings

### Modify Build Configuration

Edit `cloudbuild.yaml` to change:
- Build steps
- Deployment parameters
- Substitution variables

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check build logs
   gcloud builds log BUILD_ID
   ```

2. **Runtime Errors**:
   ```bash
   # Check Cloud Run logs
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=adk-frontend"
   ```

3. **Environment Variables Not Set**:
   - Verify environment variables in Cloud Run console
   - Check `start.sh` script execution
   - Verify `runtime-config.json` generation

### Debug Commands

```bash
# Test Docker image locally
docker run -it --entrypoint /bin/sh adk-frontend

# Check Cloud Run service status
gcloud run services describe adk-frontend --region us-central1

# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Multi-stage Builds](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/#use-multi-stage-builds)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Angular Deployment Guide](https://angular.io/guide/deployment) 