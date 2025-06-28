import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_gemini(api_key: Optional[str] = None) -> None:
    """
    Set up the Gemini API with your API key
    
    Args:
        api_key (str): Your Google AI Studio API key (optional if set as environment variable)
    """
    if api_key:
        genai.configure(api_key=api_key)
    else:
        # Try to get API key from environment variable
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Please provide an API key or set GOOGLE_API_KEY environment variable")
        genai.configure(api_key=api_key)

def chat_with_gemini(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Chat with Google's Gemini model
    
    Args:
        prompt (str): The message you want to send to Gemini
        model_name (str): The Gemini model to use
    
    Returns:
        str: Gemini's response
    """
    try:
        # Get the model
        model = genai.GenerativeModel(model_name)
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Return the response text
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}"

def chat_with_gemini_conversation(messages: list, model_name: str = "gemini-1.5-flash") -> str:
    """
    Chat with Gemini using conversation history
    
    Args:
        messages (list): List of message dictionaries with 'role' and 'content'
        model_name (str): The Gemini model to use
    
    Returns:
        str: Gemini's response
    """
    try:
        # Get the model
        model = genai.GenerativeModel(model_name)
        
        # Start a chat session
        chat = model.start_chat(history=[])
        
        # Send the last message and get response
        response = chat.send_message(messages[-1]['content'])
        
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}"

def list_available_models() -> list:
    """
    List available Gemini models
    
    Returns:
        list: List of available model names
    """
    try:
        models = genai.list_models()
        gemini_models = [model.name for model in models if 'gemini' in model.name.lower()]
        return gemini_models
    except Exception as e:
        return [f"Error listing models: {str(e)}"]

def main():
    """Main function to run the Gemini chat interface"""
    
    print("🤖 Welcome to Google Gemini Chat!")
    print("Type 'quit' to exit")
    print("Type 'models' to see available models")
    print("Type 'help' for commands")
    print("-" * 50)
    
    # Set up Gemini API
    try:
        # Option 1: Set API key directly in code (not recommended for production)
        # setup_gemini("your-api-key-here")
        
        # Option 2: Use environment variable (recommended)
        # Set this in your terminal: export GOOGLE_API_KEY="your-api-key-here"
        setup_gemini()
        
        print("✅ Gemini API configured successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up Gemini API: {e}")
        print("Please set your GOOGLE_API_KEY environment variable or provide it in the code.")
        return
    
    # Default model
    current_model = "gemini-1.5-flash"
    print(f"Using model: {current_model}")
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check if user wants to quit
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye! 👋")
            break
        
        # Check for special commands
        if user_input.lower() == 'models':
            print("\n📋 Available Gemini Models:")
            models = list_available_models()
            for i, model in enumerate(models, 1):
                print(f"{i}. {model}")
            continue
        
        if user_input.lower() == 'help':
            print("\n📖 Available Commands:")
            print("- 'quit', 'exit', 'bye': Exit the chat")
            print("- 'models': Show available Gemini models")
            print("- 'help': Show this help message")
            print("- Any other text: Send message to Gemini")
            continue
        
        # Skip empty inputs
        if not user_input:
            continue
        
        print(f"\n🤖 Gemini ({current_model}): ", end="")
        
        # Get response from Gemini
        try:
            response = chat_with_gemini(user_input, current_model)
            print(response)
        except Exception as e:
            print(f"Sorry, there was an error: {e}")

def example_usage():
    """Example of how to use the Gemini API functions"""
    
    # Set up API key
    setup_gemini("your-api-key-here")  # Replace with your actual API key
    
    # Simple chat
    response = chat_with_gemini("What is the capital of France?")
    print(f"Gemini: {response}")
    
    # Chat with conversation history
    messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
        {"role": "user", "content": "What's the weather like?"}
    ]
    
    response = chat_with_gemini_conversation(messages)
    print(f"Gemini (conversation): {response}")
    
    # List available models
    models = list_available_models()
    print(f"Available models: {models}")

if __name__ == "__main__":
    main()
