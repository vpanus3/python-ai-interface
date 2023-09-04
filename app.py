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
    conversation_dict = session.get("conversation", None)
    user_session = UserSession()
    # user_session.user_id = user_id
    # user_session.conversation = Conversation.from_dict(conversation_dict)
    # user_session.user_conversations = []

    return render_template("index.html", chat_history=conversation_dict)

@app.route("/fetch_response", methods=["POST"])
def fetch_response():
    conversation = get_conversation()
    user_message = request.form["message"]
    conversation = openai_service.send_user_message(user_message, conversation)    
    session['conversation'] = conversation.to_dict()
    # cosmos_service.save_conversation(conversation, user_id)

    return redirect(url_for("index"))

def get_conversation() -> Conversation:
    conversation_dict = session.get("conversation")
    conversation = Conversation()
    if conversation_dict is not None:
        conversation = Conversation.from_dict(conversation_dict)
    return conversation

def generate_prompt(message):
    return """ """.format(
        message
    )
