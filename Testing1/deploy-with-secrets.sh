#!/bin/bash

# HR Document Q&A - Advanced Secure Deployment Script
# This script uses Google Secret Manager for maximum security
# NO secrets are stored in files or command line arguments

set -e  # Exit on any error

# Configuration
PROJECT_ID="positive-wonder-463609-q0"  # Updated with user's project ID
SERVICE_NAME="hr-doc-qa"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Starting advanced secure deployment to Google Cloud Run..."
echo "📋 Project ID: ${PROJECT_ID}"
echo "🏷️  Service Name: ${SERVICE_NAME}"
echo "🌍 Region: ${REGION}"
echo "🔐 Using Google Secret Manager for maximum security"

# Step 1: Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project ${PROJECT_ID}

# Step 2: Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Step 3: Create secrets in Secret Manager (if they don't exist)
echo "🔐 Setting up secrets in Secret Manager..."

# Check if secrets exist, create if they don't
if ! gcloud secrets describe GEMINI_API_KEY --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo "📝 Creating GEMINI_API_KEY secret..."
    echo "Please enter your Gemini API Key:"
    read -s GEMINI_API_KEY
    echo $GEMINI_API_KEY | gcloud secrets create GEMINI_API_KEY --data-file=- --project=${PROJECT_ID}
else
    echo "✅ GEMINI_API_KEY secret already exists"
fi

if ! gcloud secrets describe GOOGLE_CLIENT_ID --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo "📝 Creating GOOGLE_CLIENT_ID secret..."
    echo "Please enter your Google OAuth Client ID:"
    read -s GOOGLE_CLIENT_ID
    echo $GOOGLE_CLIENT_ID | gcloud secrets create GOOGLE_CLIENT_ID --data-file=- --project=${PROJECT_ID}
else
    echo "✅ GOOGLE_CLIENT_ID secret already exists"
fi

if ! gcloud secrets describe GOOGLE_CLIENT_SECRET --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo "📝 Creating GOOGLE_CLIENT_SECRET secret..."
    echo "Please enter your Google OAuth Client Secret:"
    read -s GOOGLE_CLIENT_SECRET
    echo $GOOGLE_CLIENT_SECRET | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=- --project=${PROJECT_ID}
else
    echo "✅ GOOGLE_CLIENT_SECRET secret already exists"
fi

if ! gcloud secrets describe FLASK_SECRET_KEY --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo "📝 Creating FLASK_SECRET_KEY secret..."
    echo "Please enter your Flask Secret Key (or press Enter to generate one):"
    read -s FLASK_SECRET_KEY
    if [ -z "$FLASK_SECRET_KEY" ]; then
        FLASK_SECRET_KEY=$(openssl rand -hex 32)
        echo "🔑 Generated Flask Secret Key: ${FLASK_SECRET_KEY}"
    fi
    echo $FLASK_SECRET_KEY | gcloud secrets create FLASK_SECRET_KEY --data-file=- --project=${PROJECT_ID}
else
    echo "✅ FLASK_SECRET_KEY secret already exists"
fi

# Step 4: Build Docker image
echo "🏗️  Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME} --project=${PROJECT_ID}

# Step 5: Deploy to Cloud Run with Secret Manager
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,FLASK_SECRET_KEY=FLASK_SECRET_KEY:latest" \
  --project=${PROJECT_ID}

# Step 6: Get the service URL
echo "🌐 Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)" --project=${PROJECT_ID})

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌐 Your HR Document Q&A application is now live at:"
echo "   ${SERVICE_URL}"
echo ""
echo "🔐 All secrets are securely stored in Google Secret Manager"
echo "📊 You can manage secrets at: https://console.cloud.google.com/security/secret-manager?project=${PROJECT_ID}"
echo ""
echo "🚀 To update secrets in the future, use:"
echo "   gcloud secrets versions add SECRET_NAME --data-file=-"
echo ""
echo "🔄 To redeploy with updated secrets, run this script again" 