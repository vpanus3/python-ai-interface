from flask import Flask, redirect, render_template, request, url_for, session
from models.conversation_models import Conversation
from models.user_models import UserSession
from services.cosmos_service import CosmosService
from services.openai_service import OpenAIService
from services.session_service import SessionService

# TODO - system prompt - create, don't expose, store with history
# TODO - multiple conversations, export chat history

app = Flask(__name__)
app.secret_key = "f9b0216e-f1e7-4914-8652-0fbcfc0972b7" 
openai_service = OpenAIService()
cosmos_service = CosmosService()
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
    cosmos_service.save_conversation(user_session.conversation)
    return redirect(url_for("index"))

@app.route("/create_new_conversation", methods=["POST"])
def create_new_conversation():
    user_session = session_service.get_user_session()
    user_session.conversation = None

    session_service.set_user_session(user_session)
    return redirect(url_for("index"))

def generate_prompt(message):
    return """ """.format(
        message
    )
