import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

# --- ROBUST FILE PATH LOGIC & INITIALIZATION ---
cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json')
if not os.path.exists(cred_path):
    cred_path = "/app/firebase-credentials.json" 

try:
    load_dotenv()
    cred = credentials.Certificate(cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"🔴 FATAL ERROR: Could not initialize Firebase. Check credentials path and content. Error: {e}")
    db = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Createlo AI Assistant")

def load_knowledge_base():
    with open("src/kb.json", "r") as f:
        return json.load(f)
KB = load_knowledge_base()

class QueryRequest(BaseModel):
    query: str
    session_id: str

class QueryResponse(BaseModel):
    response: str
    source: str | None = None
    session_id: str

@app.get("/")
def read_root():
    return {"status": "Createlo Client Assistant API is running"}

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection is not available.")

    session_id = request.session_id
    client_query = request.query
    
    history_ref = db.collection('sessions').document(session_id).collection('history').order_by('timestamp').stream()
    conversation_history_str = "\n".join([f"Role: {msg.get('role')}, Message: {msg.get('content')}" for msg in history_ref])

    found_service = None
    for service in KB:
        for keyword in service["keywords"]:
            if keyword in client_query.lower():
                found_service = service
                break
        if found_service:
            break

    if not found_service:
        all_service_names = ", ".join([s['service_name'] for s in KB])
        prompt_context = f"The user is asking a general question. Our available services are: {all_service_names}. You should list these services to the user."
    else:
        prompt_context = f"Service Name: {found_service['service_name']}. Service Description: {found_service['description']}"
    
    # --- NEW: Final prompt with number confirmation logic ---
    full_prompt = f"""You are the official AI Assistant for Createlo. Your tone is professional, knowledgeable, and helpful.

    **CRITICAL INSTRUCTION:**
    1. If a user asks to speak to someone, book a call, or schedule a consultation, offer two options: taking their number for a callback OR providing Createlo's main contact number. Your response should be: "Of course. Our team would be happy to speak with you. I can take your number for a callback, or you can call our main office directly at +91 95611 66109. What would you prefer?"
    2. If the user provides a phone number for a callback, your next step is to **repeat the number back to them for confirmation**. Your response must be: "Great, I have that down as [The User's Phone Number]. Is that correct?"
    3. If the user confirms the number is correct (e.g., they say "yes" or "correct"), your final response should be: "Thank you. I have noted down your request for a callback. A team member will be in touch shortly. Is there anything else I can assist you with?"

    For all other questions, use the provided CONTEXT to give a helpful, conversational answer.

    CONTEXT:
    ---
    {prompt_context}
    ---
    
    CONVERSATION HISTORY:
    ---
    {conversation_history_str}
    ---

    CLIENT'S CURRENT QUESTION: "{client_query}"

    YOUR PROFESSIONAL RESPONSE:
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        stream = model.generate_content(full_prompt, stream=True)
        ai_response_text = ""
        for chunk in stream:
            ai_response_text += chunk.text
        ai_response_text = ai_response_text.strip()

        try:
            session_ref = db.collection('sessions').document(session_id)
            session_ref.collection('history').add({'role': 'Client', 'content': client_query, 'timestamp': firestore.SERVER_TIMESTAMP})
            session_ref.collection('history').add({'role': 'Assistant', 'content': ai_response_text, 'timestamp': firestore.SERVER_TIMESTAMP})
            print(f"✅ Successfully wrote to Firestore for session: {session_id}")
        except Exception as e:
            print(f"🔴 FAILED to write to Firestore for session: {session_id}. Error: {e}")

        return QueryResponse(response=ai_response_text, source=found_service['service_name'] if found_service else "General Inquiry", session_id=session_id)
    except Exception as e:
        print(f"🔴 An error occurred with the Gemini API: {e}")
        raise HTTPException(status_code=500, detail="There was an issue with the Gemini API.")

@app.get("/history/{session_id}")
def get_history(session_id: str):
    if db is None:
        return []
    try:
        docs = db.collection('sessions').document(session_id).collection('history').order_by('timestamp').stream()
        history = []
        for doc in docs:
            data = doc.to_dict()
            role = "user" if data.get("role") == "Client" else "assistant"
            history.append({"role": role, "content": data.get("content")})
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []