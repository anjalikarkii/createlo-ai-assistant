import streamlit as st
import requests
import random
import string

# --- Page Configuration ---
st.set_page_config(page_title="Createlo Assistant", page_icon="🤖")

# --- API Configuration ---
# This URL should be http://127.0.0.1:8000 for local testing,
# or your public Google Cloud Run URL after deployment.
API_BASE_URL = "http://127.0.0.1:8000"

# --- Function to load history ---
def load_chat_history(session_id):
    try:
        response = requests.get(f"{API_BASE_URL}/history/{session_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Could not load history, may be a new session. Error: {e}")
        return []

# --- Session ID Handling (persists on refresh) ---
def get_session_id():
    if 'session_id' in st.session_state:
        return st.session_state.session_id
    
    query_params = st.query_params
    if 'session_id' in query_params:
        session_id = query_params['session_id']
        st.session_state.session_id = session_id
        return session_id
    
    session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    st.session_state.session_id = session_id
    st.query_params['session_id'] = session_id
    return session_id

# Initialize session_id
session_id = get_session_id()

# Load messages for the first time
if 'messages' not in st.session_state:
    st.session_state.messages = load_chat_history(session_id)


# --- UI Rendering ---
st.title("🤖 Createlo AI Assistant")
st.write(f"Welcome! Ask me anything about our services. (Session ID: `{session_id}`)")

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Logic ---
if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        final_response = "" # Initialize a variable for the final message

        try:
            payload = {"query": prompt, "session_id": session_id}
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            response.raise_for_status()

            ai_response = response.json().get("response", "").strip()

            # --- NEW: LOGIC TO HANDLE THE TRANSFER COMMAND ---
            if "ACTION: TRANSFER_CALL" in ai_response:
                # If we get the transfer command, show a helpful message instead of the raw command.
                # You can customize this message.
                final_response = "Great! To schedule your free consultation, the best next step is to speak with a team member. Please call us at your convenience at **[Your Company Phone Number]**, or I can have someone reach out if you'd like to provide your email address."
                message_placeholder.markdown(final_response)
            else:
                # Otherwise, show the normal AI response.
                final_response = ai_response
                message_placeholder.markdown(final_response)

        except requests.exceptions.RequestException as e:
            error_message = f"I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment. (Error: Could not connect to the backend.)"
            message_placeholder.markdown(error_message)
            final_response = error_message

    # Add the final, user-friendly response to chat history
    st.session_state.messages.append({"role": "assistant", "content": final_response})