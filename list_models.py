import os
import google.generativeai as genai
from dotenv import load_dotenv

print("--- Attempting to list available models ---")

# Load the .env file to get the API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("🔴 ERROR: Could not find GEMINI_API_KEY in your .env file.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("\n✅ Found the following models available for your API key:")
        print("-------------------------------------------------------")
        
        # Loop through all available models and print their names
        for m in genai.list_models():
            # We are looking for models that support the 'generateContent' method
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
        
        print("-------------------------------------------------------")
        print("\nInstructions: Find a model name from the list above (e.g., 'models/gemini-pro') and use that exact name in your main.py file.")

    except Exception as e:
        print(f"\n🔴 FAILED: An error occurred while trying to list models.")
        print(f"Error Details: {e}")