# session_service.py

from flask import Flask, redirect, render_template, request, url_for, session
from models.user_models import UserSession
from services.conversation_service import ConversationService

class SessionService:

    def __init__(self):
        self.conversation_service = ConversationService()
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
            self.set_user_session(user_session)
        return user_session
    
    def set_conversation_id(self, conversation_id: str | None):
        user_session = self.get_user_session()
        user_session.conversation_id = conversation_id
        self.set_user_session(user_session)
        