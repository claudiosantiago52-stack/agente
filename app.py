import os
import threading
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
        session = client.beta.sessions.create(
            agent=AGENT_ID,
            environment_id=ENVIRONMENT_ID,
            title=f"WhatsApp - {phone_number}"
        )
        sessions[phone_number] = session.id
    return sessions[phone_number]

def get_agent_reply(session_id, user_text):
    """Envia mensagem e aguarda resposta do agente."""
    # Abre stream ANTES de enviar a mensagem
    reply_parts = []

    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        # Envia a mensagem do usuário
        threading.Thread(target=lambda: client.beta.sessions.events.send(
            session_id=session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_text}]}]
        )).start()

        # Coleta a resposta
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if hasattr(block, "text"):
                        reply_parts.append(block.text)
            elif event.type == "session.status_idle":
                break

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
