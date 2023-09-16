from flask import Flask, redirect, render_template, request, url_for, session
from models.conversation_models import Conversation
from models.user_models import UserSession, UserConversation
from services.conversation_service import ConversationService
from services.openai_service import OpenAIService
from services.session_service import SessionService

# TODO - system prompt - create, don't expose, store with history
# TODO - multiple conversations, export chat history

app = Flask(__name__)
app.secret_key = "f9b0216e-f1e7-4914-8652-0fbcfc0972b7" 
openai_service = OpenAIService()
conversation_service = ConversationService()
session_service = SessionService()

@app.route("/", methods=["GET"])
def index():
    user_session = session_service.get_user_session()
    return render_template("index.html", user_session=user_session.to_dict())

@app.route("/session", methods=["GET"])
def session_get() -> UserSession:
    return session_service.get_user_session().to_dict()

@app.route("/conversation", methods=["POST"])
def conversation_post():
    user_message = request.form["message"]
    user_session = session_service.get_user_session()
    conversation = user_session.conversation or Conversation()
    conversation = openai_service.send_user_message(
        user_id=user_session.user_id, 
        user_message=user_message, 
        conversation=conversation)    
    user_session.conversation = conversation
    session_service.set_user_session(user_session)
    conversation_service.save_conversation(user_session.conversation)
    return redirect(url_for("index"))

@app.route("/conversation/create", methods=["POST"])
def conversation_create():
    user_session = session_service.get_user_session()
    user_session.conversation = None
    conversation = conversation_service.create_conversation(user_session.user_id)
    user_session.conversation = conversation
    user_conversation = UserConversation.from_conversation(conversation)
    user_session.user_conversations.append(user_conversation)
    session_service.set_user_session(user_session)
    return redirect(url_for("index"))

def generate_prompt(message):
    return """ """.format(
        message
    )
