import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n🔍 Listing available Gemini models...")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✓ {model.name}")
    
    # Test generation
    print("\n🤖 Testing Gemini generation...")
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content("Say hello in 5 words")
    print(f"✓ Success! Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
