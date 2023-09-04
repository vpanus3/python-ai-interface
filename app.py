import os

import openai
from flask import Flask, redirect, render_template, request, url_for, session
from models.conversation import Conversation
from models.user import UserSession
from services.cosmos_service import CosmosService
from services.openai_service import OpenAIService

# TODO - system prompt - create, don't expose, store with history
# TODO - multiple conversations, export chat history

app = Flask(__name__)
app.secret_key = "f9b0216e-f1e7-4914-8652-0fbcfc0972b7" 
openai_service = OpenAIService()
cosmos_service = CosmosService()

# Default User Id - Authentication will be implemented later
user_id = "48f9f0e7-3312-425b-8281-4f72ab9a1419"
user_conversations = []

@app.route("/", methods=["GET"])
def index():
    user_session = get_user_session()
    return render_template("index.html", user_session=user_session.to_dict())

@app.route("/fetch_response", methods=["POST"])
def fetch_response():
    user_message = request.form["message"]
    user_session = get_user_session()
    conversation = user_session.conversation or Conversation()
    conversation = openai_service.send_user_message(
        user_id=user_session.user_id, 
        user_message=user_message, 
        conversation=conversation)    
    user_session.conversation = conversation
    set_user_session(user_session)
    cosmos_service.save_conversation(user_session.conversation)
    return redirect(url_for("index"))

def set_user_session(user_session: UserSession):
    session['user_session'] = user_session.to_dict()

def get_user_session() -> UserSession:
    user_session_dict = session.get("user_session")
    user_session = UserSession()
    if user_session_dict is not None:
        user_session = UserSession.from_dict(user_session_dict)
    else:
        user_session = UserSession()
        user_session.user_id = user_id   # TODO - figure out authentication
        user_conversations = cosmos_service.get_user_conversations(user_session.user_id)
        if (user_conversations and len(user_conversations) > 0):
            user_session.user_conversations = user_conversations
            user_conversation = user_conversations[0]
            conversation = cosmos_service.get_conversation(
                user_id=user_conversation.user_id,
                conversation_id=user_conversation.conversation_id
            )
            if conversation is not None:
                user_session.conversation = conversation
        set_user_session(user_session)

    return user_session

def generate_prompt(message):
    return """ """.format(
        message
    )
