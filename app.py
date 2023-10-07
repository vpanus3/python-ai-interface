import asyncio
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_socketio import SocketIO, emit
from models.conversation_models import Conversation
from models.user_models import UserSession, UserState
from services.conversation_service import ConversationService
from services.openai_service import OpenAIService
from services.session_service import SessionService
from services.state_service import StateService

# TODO - system prompt - create, don't expose, store with history
# TODO - export chat history
# TODO - Need a loading state for when waiting for message submit
# TODO - Streaming, stop generation
# TODO - Manage max tokens of 4097 for chatgpt 3.5

app = Flask(__name__)
app.secret_key = "f9b0216e-f1e7-4914-8652-0fbcfc0972b7" 
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5000")
openai_service = OpenAIService()
conversation_service = ConversationService()
session_service = SessionService()
state_service = StateService()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/session", methods=["GET"])
def session_get() -> UserSession:
    return session_service.get_user_session().to_dict()

@app.route("/state", methods=["GET"])
def state_get() -> UserState:
    return state_service.get_user_state().to_dict()

@app.route("/conversation/message", methods=["POST"])
def conversation_post() -> UserState:
    user_message = request.form["message"]
    user_state = state_service.get_user_state()
    conversation = user_state.conversation or Conversation()
    conversation = openai_service.send_user_message(
        user_id=user_state.user_id, 
        user_message=user_message, 
        conversation=conversation)    
    conversation = conversation_service.save_conversation(conversation)
    user_state = state_service.on_conversation_message(conversation)
    return jsonify(user_state.to_dict())

@app.route("/conversation/stream", methods=["POST"])
def conversation_stream():
    user_message = request.form["message"]
    user_state = state_service.get_user_state()
    conversation = user_state.conversation or Conversation()
    conversation = openai_service.stream_user_message(
        user_id=user_state.user_id, 
        user_message=user_message, 
        conversation=conversation,
        stream_handler=conversation_stream_handler)
    return jsonify({ "message": "conversation stream started" })

def conversation_stream_handler(conversation: Conversation, finished: bool):
    # send serializable object to websocket, async issues..
    if (finished): conversation = conversation_service.save_conversation(conversation)
    user_state = state_service.on_conversation_message(conversation)
    socketio.emit('user_state', user_state.to_dict())

@app.route("/conversation/create", methods=["POST"])
def conversation_create():
    user_session = session_service.get_user_session()
    conversation = conversation_service.create_conversation(user_session.user_id)
    user_state = state_service.on_conversation_created(conversation)
    return jsonify(user_state.to_dict())

@app.route("/conversation/switch", methods=["POST"])
def conversation_switch():
    conversation_id = request.args.get('conversation_id', None)
    user_session = session_service.get_user_session()
    conversation = conversation_service.get_conversation(
        user_id=user_session.user_id,
        conversation_id=conversation_id
    )
    user_state = state_service.on_conversation_switch(conversation)
    return jsonify(user_state.to_dict())

@app.route("/conversation/delete", methods=["DELETE"])
def conversation_delete():
    deleted_conversation_id = request.args.get('conversation_id', None)
    user_session = session_service.get_user_session()
    conversation_service.delete_conversation(
        user_id=user_session.user_id,
        conversation_id=deleted_conversation_id
    )
    user_state = state_service.on_conversation_deleted(deleted_conversation_id)
    return jsonify(user_state.to_dict())

@app.route("/conversation/rename", methods=["PUT"])
def conversation_rename():
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    title = data.get('title')
    user_session = session_service.get_user_session()
    conversation = conversation_service.rename_conversation(
        user_id=user_session.user_id,
        conversation_id=conversation_id,
        title=title
    )
    user_state = state_service.on_conversation_rename(conversation)
    return jsonify(user_state.to_dict())

@socketio.on('connect')
def handle_connect():
    emit('server_response', {'message': 'Greetings from the Server realm!'})

if __name__ == '__main__':
    socketio.run(app)