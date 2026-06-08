import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

AGENT_ID = os.environ["AGENT_ID"]          # ID do seu agente
ENVIRONMENT_ID = os.environ["ENVIRONMENT_ID"]  # ID do seu environment

# Mapeia número de telefone → session_id
sessions = {}

def get_or_create_session(phone_number):
    if phone_number not in sessions:
        session = client.beta.agents.sessions.create(
            agent_id=AGENT_ID,
        )
        sessions[phone_number] = session.id
    return sessions[phone_number]

def get_agent_reply(session_id, user_text):
    """Envia mensagem e aguarda resposta do agente."""
    reply_parts = []

    response = client.beta.agents.sessions.events.create(
        agent_id=AGENT_ID,
        session_id=session_id,
        event={
            "type": "user_turn",
            "content": [{"type": "text", "text": user_text}],
        },
    )

    # Collect text from all assistant content blocks in the response
    for event in response.events if hasattr(response, "events") else []:
        if getattr(event, "type", None) == "assistant_turn":
            for block in getattr(event, "content", []):
                if hasattr(block, "text"):
                    reply_parts.append(block.text)

    return "".join(reply_parts) or "Desculpe, não consegui processar sua mensagem."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    session_id = get_or_create_session(sender)
    reply_text = get_agent_reply(session_id, incoming_msg)

    # Twilio espera TwiML como resposta
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
