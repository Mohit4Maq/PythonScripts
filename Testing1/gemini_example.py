#!/usr/bin/env python3
"""
Simple example of using Google's Gemini AI API
This script demonstrates basic usage of the Gemini API
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def simple_gemini_example():
    """Simple example of using Gemini API"""
    
    # Set your API key (replace with your actual API key)
    # Option 1: Set directly (not recommended for production)
    # API_KEY = "your-api-key-here"  # Replace with your actual API key
    
    # Option 2: Use environment variable from .env file (recommended)
    API_KEY = os.getenv('GOOGLE_API_KEY')
    
    if not API_KEY:
        print("❌ Please set GOOGLE_API_KEY in your .env file")
        print("   Format: GOOGLE_API_KEY=your-actual-api-key-here")
        return
    
    # Configure the API
    genai.configure(api_key=API_KEY)
    
    # Create a model instance
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Example 1: Simple text generation
    print("🤖 Example 1: Simple text generation")
    print("-" * 40)
    
    prompt = "Write a short poem about artificial intelligence"
    response = model.generate_content(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response.text}")
    print()
    
    # Example 2: Chat conversation
    print("🤖 Example 2: Chat conversation")
    print("-" * 40)
    
    chat = model.start_chat(history=[])
    
    # First message
    response1 = chat.send_message("Hello! What can you do?")
    print(f"User: Hello! What can you do?")
    print(f"Gemini: {response1.text}")
    print()
    
    # Follow-up message
    response2 = chat.send_message("Can you help me write code?")
    print(f"User: Can you help me write code?")
    print(f"Gemini: {response2.text}")
    print()
    
    # Example 3: Different models
    print("🤖 Example 3: Available models")
    print("-" * 40)
    
    try:
        models = genai.list_models()
        gemini_models = [model.name for model in models if 'gemini' in model.name.lower()]
        print("Available Gemini models:")
        for i, model_name in enumerate(gemini_models, 1):
            print(f"{i}. {model_name}")
    except Exception as e:
        print(f"Error listing models: {e}")
    
    print()
    print("✅ Examples completed!")

def get_api_key_instructions():
    """Print instructions for getting an API key"""
    print("🔑 How to get your Google AI Studio API key:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated API key")
    print("5. Add it to your .env file: GOOGLE_API_KEY=your-key")
    print()

if __name__ == "__main__":
    print("🚀 Google Gemini AI API Example")
    print("=" * 50)
    print()
    
    get_api_key_instructions()
    
    # Check if API key is set
    if os.getenv('GOOGLE_API_KEY'):
        print("✅ Found GOOGLE_API_KEY in .env file")
        simple_gemini_example()
    else:
        print("❌ No GOOGLE_API_KEY found in .env file")
        print("   Please add your API key to the .env file:")
        print("   GOOGLE_API_KEY=your-api-key-here")
        print()
        simple_gemini_example() 