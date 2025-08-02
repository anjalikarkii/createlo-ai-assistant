import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the .env file to get the API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("🔴 ERROR: Could not find GEMINI_API_KEY in your .env file.")
else:
    print("🟢 API Key found successfully.")
    
    try:
        # Configure the Gemini client
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("🟡 Attempting to connect to Google Gemini...")
        
        # Create a model and ask a simple question
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("What is the color of the sky?")
        
        # If we get here, it worked!
        print("\n✅ SUCCESS! Connected to Gemini and received a response.")
        print("-------------------------------------------------------")
        print(f"AI Response: {response.text.strip()}")
        print("-------------------------------------------------------")

    except Exception as e:
        # If there's any error during the connection or API call
        print(f"\n🔴 FAILED: An error occurred while trying to connect to Gemini.")
        print(f"Error Details: {e}")