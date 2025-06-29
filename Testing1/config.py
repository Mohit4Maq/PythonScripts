# Configuration file for HR Document Q&A System
import os
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path, override any existing)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id-here")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET_KEY", "your-google-client-secret-here")

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "your-gemini-api-key-here")

# Flask Configuration
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "3cad09e8ab2346284083fdc8eaed5391fdb35da69d5a40b219b85effc47823f9")

# Instructions:
# 1. The .env file contains the actual credentials with these variable names:
#    - GOOGLE_API_KEY (for Gemini AI)
#    - GOOGLE_CLIENT_ID (for Google OAuth)
#    - GOOGLE_CLIENT_SECRET_KEY (for Google OAuth)
#    - FLASK_SECRET_KEY (for Flask sessions)
# 2. This config file automatically loads from .env file
# 3. Never modify the .env file directly - it contains sensitive credentials 