from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests

app = Flask(__name__)

BACKEND_API_URL = "http://localhost:8000/query"

@app.route("/voice", methods=['POST'])
def handle_call():
    """Handles the entire conversational call flow."""
    resp = VoiceResponse()
    speech_result = request.form.get('SpeechResult')
    session_id = request.form['CallSid']

    if speech_result:
        # User has said something, so we process it.
        try:
            payload = {"query": speech_result, "session_id": session_id}
            backend_response = requests.post(BACKEND_API_URL, json=payload, timeout=15)
            backend_response.raise_for_status()
            
            ai_answer = backend_response.json().get("response", "I seem to be having a slight issue at the moment.").strip()
            
            # Speak the AI's response (which could be an answer, or a request for a number)
            resp.say(ai_answer)
            
            # Always listen for the next thing the user has to say
            gather = Gather(input='speech', action='/voice', method='POST', timeout=7)
            resp.append(gather)
            
            # This plays if the user goes silent after the AI speaks.
            resp.say("I didn't hear anything. If you need no further assistance, thank you for your call. Goodbye.")
            resp.hangup()

        except requests.exceptions.RequestException as e:
            print(f"ERROR calling backend: {e}")
            resp.say("I apologize, I'm having a technical issue connecting to our main system. Please try again later.")
            resp.hangup()
    else:
        # This is the first turn of the call (user hasn't spoken yet).
        gather = Gather(input='speech', action='/voice', method='POST', timeout=5)
        gather.say(
            'Thank you for calling Createlo. You are speaking with the official AI assistant. How may I assist you today?'
        )
        resp.append(gather)
        # This message plays if the user is silent after the initial greeting.
        resp.say("I'm sorry, I didn't hear anything. Please call back if you need assistance. Goodbye.")
        resp.hangup()

    return Response(str(resp), mimetype='application/xml')

if __name__ == "__main__":
    app.run(port=5001)