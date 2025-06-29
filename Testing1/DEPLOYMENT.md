# HR Document Q&A - Secure Deployment Guide

This guide explains how to deploy your HR Document Q&A application to Google Cloud Run **without hardcoding sensitive keys** in the deployment command.

## 🚨 Why We Don't Hardcode Secrets

The original deployment command you saw was **insecure** because it hardcoded API keys directly in the command line:

```bash
# ❌ INSECURE - Don't do this!
gcloud run deploy hr-doc-qa \
  --set-env-vars "GEMINI_API_KEY=your_key,GOOGLE_CLIENT_ID=your_id,GOOGLE_CLIENT_SECRET=your_secret,FLASK_SECRET_KEY=your_flask_secret"
```

**Problems with this approach:**
- Secrets are visible in command history
- Secrets are logged in system logs
- Secrets are stored in plain text
- No secret rotation capability
- Security audit nightmare

## 🔒 Secure Deployment Options

### Option 1: Environment Variables File (Recommended for Development)

Use a `.env.yaml` file that gets deleted after deployment:

```bash
# Create .env.yaml (don't commit this file!)
cat > .env.yaml << EOF
GEMINI_API_KEY: "your-actual-gemini-key"
GOOGLE_CLIENT_ID: "your-actual-client-id"
GOOGLE_CLIENT_SECRET: "your-actual-client-secret"
SECRET_KEY: "your-actual-flask-secret"
OAUTHLIB_INSECURE_TRANSPORT: "0"
EOF

# Deploy using the file
gcloud run deploy hr-doc-qa \
  --image gcr.io/YOUR_PROJECT_ID/hr-doc-qa \
  --env-vars-file .env.yaml

# Clean up
rm .env.yaml
```

### Option 2: Google Secret Manager (Recommended for Production)

Store secrets in Google Secret Manager for maximum security:

```bash
# Store secrets in Secret Manager
echo "your-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
echo "your-client-secret" | gcloud secrets create google-client-secret --data-file=-
echo "your-flask-secret" | gcloud secrets create flask-secret-key --data-file=-

# Deploy using Secret Manager references
gcloud run deploy hr-doc-qa \
  --image gcr.io/YOUR_PROJECT_ID/hr-doc-qa \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,GOOGLE_CLIENT_SECRET=google-client-secret:latest,SECRET_KEY=flask-secret-key:latest"
```

## 🚀 Quick Deployment

### Prerequisites

1. **Google Cloud SDK** installed
2. **Docker** installed (optional, Cloud Build will handle this)
3. **Google Cloud Project** with billing enabled

### Step-by-Step Deployment

1. **Clone and prepare your project:**
   ```bash
   git clone <your-repo>
   cd <your-project>
   ```

2. **Choose your deployment method:**

   **For Development/Testing:**
   ```bash
   ./deploy.sh
   ```

   **For Production (with Secret Manager):**
   ```bash
   ./deploy-with-secrets.sh
   ```

3. **Update Google Cloud Console:**
   - Go to Google Cloud Console → APIs & Services → Credentials
   - Edit your OAuth 2.0 Client ID
   - Add your Cloud Run URL to authorized redirect URIs:
     ```
     https://your-service-url/login/google/authorized
     ```

## 📋 Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ |
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth Client Secret | ✅ |
| `SECRET_KEY` | Flask session secret key | ✅ |
| `OAUTHLIB_INSECURE_TRANSPORT` | Set to "0" for production | ✅ |

## 🔧 Docker Configuration

The `Dockerfile` includes:

- **Security**: Non-root user, minimal base image
- **Optimization**: Multi-stage build, layer caching
- **Health checks**: Automatic health monitoring
- **Production ready**: Proper environment variables

## 🛡️ Security Best Practices

1. **Never hardcode secrets** in deployment commands
2. **Use Secret Manager** for production deployments
3. **Rotate secrets regularly**
4. **Enable audit logging**
5. **Use least privilege access**
6. **Monitor secret access**

## 🔍 Troubleshooting

### Common Issues

1. **"Permission denied" errors:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **"API not enabled" errors:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

3. **"Redirect URI mismatch" errors:**
   - Update your Google Cloud Console OAuth settings
   - Use the exact Cloud Run URL

### Debugging

```bash
# Check service status
gcloud run services describe hr-doc-qa --region us-central1

# View logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=hr-doc-qa"

# Test locally
docker build -t hr-doc-qa .
docker run -p 8080:8080 -e GEMINI_API_KEY=your-key hr-doc-qa
```

## 📊 Monitoring and Scaling

### Resource Configuration

```bash
# Adjust resources as needed
gcloud run services update hr-doc-qa \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0
```

### Monitoring Setup

1. **Enable Cloud Monitoring**
2. **Set up alerts** for errors and performance
3. **Monitor secret access** in Secret Manager
4. **Track API usage** for Gemini

## 🔄 Updating Secrets

### Using Secret Manager

```bash
# Update a secret
echo "new-secret-value" | gcloud secrets versions add gemini-api-key --data-file=-

# The service will automatically use the latest version
```

### Using Environment Variables

```bash
# Update environment variables
gcloud run services update hr-doc-qa \
  --set-env-vars "GEMINI_API_KEY=new-key"
```

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Flask-Dance Documentation](https://flask-dance.readthedocs.io/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)

## 🆘 Support

If you encounter issues:

1. Check the logs: `gcloud logs read`
2. Verify environment variables are set correctly
3. Ensure all APIs are enabled
4. Check OAuth redirect URI configuration
5. Verify Secret Manager permissions

---

**Remember**: Security is not optional. Always use secure methods to handle secrets and never hardcode them in your deployment commands! 