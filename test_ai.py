# test_ai.py
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Testing AI Connection")
print("=" * 50)

# Check environment
print(f"\n1. Checking environment:")
print(f"   USE_AI = {os.getenv('USE_AI', 'not set')}")
print(f"   GEMINI_API_KEY = {'set' if os.getenv('GEMINI_API_KEY') else 'not set'}")

# Try importing
print("\n2. Checking imports:")
try:
    import google.generativeai as genai
    print("   ✓ google-generativeai imported")
except ImportError as e:
    print(f"   ✗ google-generativeai not installed: {e}")

# Try configuring
print("\n3. Configuring Gemini:")
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("   ✓ Gemini configured successfully")
        
        # Test API call
        print("\n4. Testing API call:")
        response = model.generate_content("Say 'Hello, AI is working!'")
        print(f"   ✓ API response: {response.text[:50]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
else:
    print("   ✗ No API key found in .env file")

print("\n" + "=" * 50)
