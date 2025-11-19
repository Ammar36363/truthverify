import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        
        print("🔄 Fetching available models...")
        models = genai.list_models()
        
        print("📋 AVAILABLE MODELS:")
        for model in models:
            print(f"✅ Model: {model.name}")
            print(f"   Supported methods: {model.supported_generation_methods}")
            print("---")
            
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No API key found")