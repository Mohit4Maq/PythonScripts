# Configuration file for HR Document Q&A System
import os
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path, override any existing)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id-here")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret-here")

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")

# Flask Configuration
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "3cad09e8ab2346284083fdc8eaed5391fdb35da69d5a40b219b85effc47823f9")

# Email configuration for OTP sending
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail").lower()  # gmail, outlook, yahoo, custom

# Email provider configurations
EMAIL_CONFIGS = {
    "gmail": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "use_tls": True,
        "use_ssl": False
    },
    "outlook": {
        "smtp_server": "smtp-mail.outlook.com", 
        "smtp_port": 587,
        "use_tls": True,
        "use_ssl": False
    },
    "yahoo": {
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "use_tls": True,
        "use_ssl": False
    },
    "custom": {
        "smtp_server": os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
        "use_tls": os.getenv("EMAIL_USE_TLS", "true").lower() == "true",
        "use_ssl": os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
    }
}

# Get email configuration based on provider
EMAIL_CONFIG = EMAIL_CONFIGS.get(EMAIL_PROVIDER, EMAIL_CONFIGS["gmail"])

# Email credentials
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-app-password")
EMAIL_FROM = os.getenv("EMAIL_FROM", "your-email@gmail.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "HR Document Q&A System")

# Email settings
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "30"))
EMAIL_MAX_RETRIES = int(os.getenv("EMAIL_MAX_RETRIES", "3"))

# Instructions:
# 1. The .env file contains the actual credentials with these variable names:
#    - GEMINI_API_KEY (for Gemini AI)
#    - GOOGLE_CLIENT_ID (for Google OAuth)
#    - GOOGLE_CLIENT_SECRET_KEY (for Google OAuth)
#    - FLASK_SECRET_KEY (for Flask sessions)
#    - EMAIL_USERNAME (your email address)
#    - EMAIL_PASSWORD (your app password)
#    - EMAIL_FROM (sender email address)
#    - EMAIL_ENABLED (set to "true" to enable real email sending)
#    - EMAIL_PROVIDER (gmail, outlook, yahoo, or custom)
# 2. This config file automatically loads from .env file
# 3. Never modify the .env file directly - it contains sensitive credentials 