import os

import openai
from flask import Flask, redirect, render_template, request, url_for, session
from models.openai_models import ChatMessage, ChatCompletionRequest, ChatRole, ChatCompletionResponse
from models.conversation import Conversation, ConversationMessage
from services.cosmosdb import CosmosClientWrapper
from services.openai_service import OpenAIService

# TODO - system prompt - create, don't expose, store with history
# TODO - multiple conversations, export chat history

app = Flask(__name__)
app.secret_key = "f9b0216e-f1e7-4914-8652-0fbcfc0972b7" 
openai_service = OpenAIService()

# Default User Id - Authentication will be implemented later
user_id = "48f9f0e7-3312-425b-8281-4f72ab9a1419"

@app.route("/", methods=["GET"])
def index():
    converation = session.get("chat_history")
    return render_template("index.html", chat_history=converation)

@app.route("/fetch_response", methods=["POST"])
def fetch_response():
    conversation = get_conversation()
    user_message = request.form["message"]
    conversation = openai_service.send_user_message(user_message, conversation)    
    session['chat_history'] = conversation.to_dict()
    return redirect(url_for("index"))

def get_conversation() -> Conversation:
    converation_dict = session.get("chat_history")
    converation = Conversation()
    if (converation_dict is not None):
        converation = Conversation.from_dict(converation_dict)
    return converation

def generate_prompt(message):
    return """ """.format(
        message
    )
