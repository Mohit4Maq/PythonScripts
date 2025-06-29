#!/usr/bin/env python3
"""
Setup script for HR Document Q&A System with Google OAuth Authentication
"""

import os
import sys

def check_config():
    """Check if configuration is properly set up"""
    print("🔍 Checking configuration...")
    
    # Check if config.py exists
    if os.path.exists('config.py'):
        print("✅ config.py file found")
    else:
        print("❌ config.py file not found")
        return False
    
    # Try to import config
    try:
        from config import GOOGLE_CLIENT_SECRET, SECRET_KEY, GEMINI_API_KEY
        print("✅ Configuration imported successfully")
        
        # Check if values are set
        if GOOGLE_CLIENT_SECRET != "your-google-client-secret-here":
            print("✅ Google Client Secret is configured")
        else:
            print("⚠️  Google Client Secret needs to be set")
            
        if GEMINI_API_KEY != "your-gemini-api-key-here":
            print("✅ Gemini API Key is configured")
        else:
            print("⚠️  Gemini API Key needs to be set")
            
        if SECRET_KEY != "your-super-secret-key-change-this-in-production":
            print("✅ Flask Secret Key is configured")
        else:
            print("⚠️  Flask Secret Key needs to be set")
            
    except ImportError as e:
        print(f"❌ Error importing config: {e}")
        return False
    
    return True

def setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("🔧 SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. 📋 GET GOOGLE CLIENT SECRET:")
    print("   • Go to: https://console.cloud.google.com/")
    print("   • Create a new project or select existing one")
    print("   • Enable Google+ API or Google Identity API")
    print("   • Go to 'APIs & Services' > 'Credentials'")
    print("   • Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   • Choose 'Web application'")
    print("   • Set authorized redirect URIs:")
    print("     - http://localhost:8080/login/google/authorized")
    print("     - http://127.0.0.1:8080/login/google/authorized")
    print("   • Copy the Client Secret (you already have the Client ID)")
    
    print("\n2. 🤖 GET GEMINI API KEY:")
    print("   • Go to: https://makersuite.google.com/app/apikey")
    print("   • Sign in with your Google account")
    print("   • Create a new API key")
    print("   • Copy the API key")
    
    print("\n3. ⚙️  CONFIGURE THE SYSTEM:")
    print("   Option A: Edit config.py file")
    print("   Option B: Set environment variables:")
    print("     export GOOGLE_CLIENT_SECRET='your-secret'")
    print("     export GEMINI_API_KEY='your-key'")
    print("     export SECRET_KEY='your-secret-key'")
    
    print("\n4. 🚀 RUN THE SYSTEM:")
    print("   python web_app_hr_bot_auth.py")
    
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("🚀 HR Document Q&A System - Authentication Setup")
    print("="*60)
    
    # Check current configuration
    config_ok = check_config()
    
    if config_ok:
        print("\n✅ Configuration looks good!")
        print("You can now run: python web_app_hr_bot_auth.py")
    else:
        print("\n❌ Configuration needs to be set up")
        setup_instructions()
    
    # Always show instructions for reference
    setup_instructions()

if __name__ == "__main__":
    main() 