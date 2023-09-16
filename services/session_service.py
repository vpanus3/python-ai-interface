# session_service.py

from flask import Flask, redirect, render_template, request, url_for, session
from models.user_models import UserSession
from services.conversation_service import ConversationService

class SessionService:

    def __init__(self):
        self.cosmos_service = ConversationService()
        # TODO Authentication
        self.user_id = "48f9f0e7-3312-425b-8281-4f72ab9a1419"

    def set_user_session(self, user_session: UserSession):
        session['user_session'] = user_session.to_dict()

    def get_user_session(self) -> UserSession:
        user_session_dict = session.get("user_session")
        user_session = UserSession()
        if user_session_dict is not None:
            user_session = UserSession.from_dict(user_session_dict)
        else:
            user_session = UserSession()
            user_session.user_id = self.user_id   # TODO - figure out authentication
            user_conversations = self.cosmos_service.get_user_conversations(user_session.user_id)
            if (user_conversations and len(user_conversations) > 0):
                user_session.user_conversations = user_conversations
                user_conversation = user_conversations[0]  #TODO - save last conversation
                conversation = self.cosmos_service.get_conversation(
                    user_id=user_conversation.user_id,
                    conversation_id=user_conversation.conversation_id
                )
                if conversation is not None:
                    user_session.conversation = conversation
            self.set_user_session(user_session)
        return user_session