# T1D-Swarm Backend Deployment Guide

## 🏗️ **Project Structure**

```
T1d-swarm/
├── .env                    # Environment variables (git-ignored)
├── frontend/               # Frontend application (future)
├── backend/                # Backend application
│   ├── deploy.sh          # Linux/macOS deployment script
│   ├── deploy.bat         # Windows deployment script
│   ├── test-deployment.sh # Deployment verification script
│   ├── cloudbuild.yaml   # Cloud Build configuration
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── t1d_swarm/
└── README.md
```

## 🚀 **Quick Deployment**

### **Prerequisites**
1. **Google Cloud CLI** installed and authenticated
2. **`.env` file** in project root with environment variables
3. **Run from backend folder** (`cd backend`)

### **Deploy Commands**

```bash
# Navigate to backend folder first
cd backend

# Windows
deploy.bat

# Linux/macOS
./deploy.sh

# With custom project/region
deploy.bat your-project-id us-west1
./deploy.sh your-project-id us-west1
```

### **Test Deployment**
```bash
# From backend folder
./test-deployment.sh https://your-service-url
```

## 🔧 **Environment Variables**

The deployment scripts read from your **root `.env`** file (../env):

```bash
# Required variables (in project root .env)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
JUDGE_CODES=CODE1,CODE2,CODE3

# AI Model Configuration
GENERATE_SCENARIO_MODEL=gemini-2.5-flash-lite-preview-06-17
AMBIENT_CONTEXT_MODEL=gemini-2.0-flash
SIMULATED_CGM_MODEL=gemini-2.0-flash
GLYCEMIC_FORECAST_MODEL=gemini-2.5-pro
FORECAST_VERIFIER_MODEL=gemini-2.5-flash
INSIGHT_PRESENTER_MODEL=gemini-2.5-flash

# Optional
GOOGLE_GENAI_USE_VERTEXAI=true
```

## 🔐 **Security Features**

- ✅ **Environment variables** loaded from root `.env` (git-ignored)
- ✅ **Judge codes** hidden in deployment output
- ✅ **Scripts are safe** to commit (no hardcoded secrets)
- ✅ **Backend-specific** deployment isolated from frontend

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **"../.env file not found"**
   - Make sure you're running from `backend/` folder
   - Check that `.env` file exists in project root (one level up)

2. **"Environment variables not found"**
   - Verify `.env` file exists in project root (`../env`)
   - Check variable names match exactly

3. **"Build failed"**
   - Check `Dockerfile` exists in backend folder
   - Verify `requirements.txt` is present in backend folder

### **Manual Deployment**

If scripts fail, you can deploy manually from backend folder:

```bash
# From backend/ directory
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/t1d-swarm .
gcloud run deploy t1d-swarm \
  --image gcr.io/YOUR_PROJECT_ID/t1d-swarm \
  --set-env-vars "JUDGE_CODES=YOUR_CODES"
```

### **Cloud Build (CI/CD)**

For automated deployment, trigger from backend folder:

```bash
# From backend/ directory
gcloud builds submit --config cloudbuild.yaml
```

## 📁 **File Locations**

| Component | Location | Purpose |
|-----------|----------|---------|
| `.env` | `../env` (root) | Environment variables |
| Backend code | `./` (backend folder) | Application source |
| Deployment scripts | `./` (backend folder) | Deploy from here |
| Frontend (future) | `../frontend/` | Separate deployment |

## 📋 **Deployment Checklist**

- [ ] Navigate to `backend/` folder
- [ ] `.env` file configured in project root
- [ ] Google Cloud CLI authenticated
- [ ] Judge codes set in root `.env`
- [ ] Project ID correct in root `.env`

## 🎯 **Usage Examples**

```bash
# Standard deployment workflow
cd backend
./deploy.sh

# Check deployment
./test-deployment.sh https://your-service-url

# Update environment and redeploy
# 1. Edit ../env file
# 2. Run ./deploy.sh again
```

Your T1D-Swarm backend is ready for deployment! 🎉

**Next Steps:**
- Deploy backend using scripts in `backend/` folder
- Add frontend deployment scripts to `frontend/` folder (future)
- Set up CI/CD pipeline using `cloudbuild.yaml` 


gcloud run deploy t1d-swarm --image gcr.io/gen-lang-client-0597970170/t1d-swarm --region us-central1 --allow-unauthenticated --set-env-vars "JUDGE_CODES=HACKJUDGE2024,JUDGE001,EVALCODE"