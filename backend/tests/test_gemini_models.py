#!/usr/bin/env python3
"""
Test available Gemini models
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_models():
    """Test which Gemini models are available"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    models_to_test = [
        'gemini-pro',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'models/gemini-pro',
        'models/gemini-1.5-pro'
    ]
    
    for model_name in models_to_test:
        try:
            print(f"Testing model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, test message")
            print(f"✅ {model_name} - Works!")
            print(f"   Response: {response.text[:50]}...")
            break  # Use the first working model
        except Exception as e:
            print(f"❌ {model_name} - Error: {str(e)[:100]}...")
    
    # List all available models
    print("\n📋 Available models:")
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  ✅ {model.name}")
    except Exception as e:
        print(f"❌ Could not list models: {e}")

if __name__ == "__main__":
    test_gemini_models()