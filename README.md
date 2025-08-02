# Createlo AI Client Assistant

This project is a multi-channel AI-powered assistant designed to serve as the first point of contact for Createlo's clients. It can handle inquiries via a web-based chat interface and a conversational telephone line. The assistant is built to be knowledgeable, professional, and capable of generating leads by capturing user information for callbacks.

## Features

- **Dual-Channel Interface:**
  - **Web Chat:** An interactive and persistent chat UI built with Streamlit.
  - **Voice Line:** A fully conversational voice bot using Twilio that can understand and respond to spoken queries.
- **Intelligent Core:** Powered by Google's Gemini Pro model for advanced natural language understanding and response generation.
- **Persistent Memory:** Utilizes Google Firebase Firestore to save and retrieve conversation histories, allowing for seamless, context-aware dialogues across sessions.
- **Lead Generation:** The AI is programmed to identify when a user is interested in a consultation and will professionally request their phone number for a callback from the Createlo team.
- **Accurate Knowledge Base:** Fueled by a `kb.json` file containing up-to-date information on all of Createlo's official services.
- **Lead Capture & Retrieval:** All conversations, including contact information provided by users, are stored securely in Firestore. The team can review these conversation logs directly in the Firebase console to follow up on new leads.

## Tech Stack

- **Backend (AI Brain):** Python, FastAPI
- **Voice Bridge:** Python, Flask
- **Web UI:** Python, Streamlit
- **AI Model:** Google Gemini
- **Database:** Google Firebase Firestore
- **Telephony:** Twilio API

## How to Run Locally

### Prerequisites

- Python 3.10+
- `git`
- A `(venv)` virtual environment is highly recommended.
- Accounts for: Google Cloud (for Gemini & Firestore) and Twilio.

### 1. Setup

Clone the repository and install the required dependencies:
```bash
git clone https://github.com/your-username/createlo-ai-assistant.git
cd createlo-ai-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt