import os

import openai
from flask import Flask, redirect, render_template, request, url_for, session
from models.openai import ChatMessage, ChatCompletionRequest, ChatHistory, ChatRole, ChatCompletionResponse, ChatHistoryMessage
from services.cosmosdb import CosmosClientWrapper

# TODO - system prompt - create, don't expose, store with history
# TODO - multiple conversations, export chat history

app = Flask(__name__)
app.secret_key = "f9b0216e-f1e7-4914-8652-0fbcfc0972b7" 
openai.api_key = os.getenv("OPENAI_API_KEY")
temperature = float(os.getenv("OPENAI_Temperature"))

# Default User Id - Authentication will be implemented later
user_id = "48f9f0e7-3312-425b-8281-4f72ab9a1419"

@app.route("/", methods=["GET"])
def index():
    wrapper = CosmosClientWrapper()
    wrapper.test()
    chat_history = session.get("chat_history")
    return render_template("index.html", chat_history=chat_history)

@app.route("/fetch_response", methods=["POST"])
def fetch_response():
    chat_message = ChatMessage(ChatRole.USER, request.form["message"])
    chat_history = get_chat_history()
    chat_request = get_chat_completion_request(chat_message, chat_history)
    response = openai.ChatCompletion.create(
        model=chat_request.model,
        messages=chat_request.get_messages_dict(),
        temperature=chat_request.temperature,
    )
    chat_completion_response = ChatCompletionResponse.from_chat_completion(response)
    chat_history = update_chat_history(chat_history, chat_message, chat_completion_response)
    session['chat_history'] = chat_history.to_dict()
    return redirect(url_for("index"))

def get_chat_history() -> ChatHistory:
    chat_history_dict = session.get("chat_history")
    chat_history = ChatHistory()
    if (chat_history_dict is not None):
        chat_history = ChatHistory.from_dict(chat_history_dict)
    return chat_history

def get_chat_completion_request(chat_message: ChatMessage, chat_history: ChatHistory) -> ChatCompletionRequest:
    messages = chat_history.get_chat_messages()
    messages.append(chat_message)
    request = ChatCompletionRequest('gpt-3.5-turbo-0613', messages, temperature)
    return request

def update_chat_history(chat_history: ChatHistory, chat_message: ChatMessage, chat_completion_response: ChatCompletionResponse) -> ChatHistory:
    chat_history = chat_history or ChatHistory()
    chat_history_message_request = ChatHistoryMessage(
        chat_message.content,
        chat_message.role,
        chat_completion_response.created,
        chat_completion_response.model,
        temperature,
        chat_completion_response.choices[0].finish_reason
    )
    chat_history.messages.append(chat_history_message_request)
    chat_history_message_response = ChatHistoryMessage(
        chat_completion_response.choices[0].message.content,
        chat_completion_response.choices[0].message.role,
        chat_completion_response.created,
        chat_completion_response.model,
        temperature,
        chat_completion_response.choices[0].finish_reason
    )
    chat_history.messages.append(chat_history_message_response)
    return chat_history

def generate_prompt(message):
    return """ """.format(
        message
    )
