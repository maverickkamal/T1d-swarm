@echo off
echo 🔧 Fixing Cloud Run permissions for public access...

gcloud run services add-iam-policy-binding adk-frontend ^
    --member=allUsers ^
    --role=roles/run.invoker ^
    --region=us-central1 ^
    --project=gen-lang-client-0597970170

if errorlevel 1 (
    echo ❌ Failed to set permissions
    exit /b 1
)

echo ✅ Permissions updated! Your service is now publicly accessible.
echo 🌐 Service URL: https://adk-frontend-993662266913.us-central1.run.app 