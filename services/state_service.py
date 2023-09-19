# state_service.py

from models.user_models import UserState, UserConversation
from models.conversation_models import Conversation
from services.session_service import SessionService
from services.conversation_service import ConversationService

class StateService:
    def __init__(self):
        self.session_service = SessionService()
        self.conversation_service = ConversationService()

    def get_user_state(self) -> UserState:
        user_state = UserState()
        user_session = self.session_service.get_user_session()
        user_state.user_id = user_session.user_id
        user_state.user_conversations = self.conversation_service.get_user_conversations(user_session.user_id)       
        conversation_id = None
        if (user_session.conversation_id):
            user_conversation = next((user_conversation for user_conversation in user_state.user_conversations if user_conversation.conversation_id == user_session.conversation_id), None)
            if (user_conversation is not None):
                conversation_id = user_conversation.conversation_id
        elif (user_state.user_conversations and len(user_state.user_conversations) > 0):
            conversation_id = user_state.user_conversations[0].conversation_id

        if (conversation_id is not None):
            conversation = self.conversation_service.get_conversation(
                user_id=user_session.user_id,
                conversation_id=conversation_id
            )
            if conversation is not None:
                user_state.conversation = conversation
                conversation_id = conversation.id
        self.session_service.set_conversation_id(conversation_id)
        return user_state
    
    def on_conversation_message(self, conversation: Conversation) -> UserState:
        user_state = self.get_user_state()
        user_state.conversation = conversation
        if (conversation is not None):
            for index, user_conversation in enumerate(user_state.user_conversations):
                if user_conversation.conversation_id == conversation.id:
                    updated_user_conversation = UserConversation.from_conversation(conversation)
                    user_state.user_conversations[index] = updated_user_conversation
                    break
            self.session_service.set_conversation_id(conversation.id)
        return user_state
    
    def on_conversation_switch(self, conversation: Conversation) -> UserState:
        user_state = self.get_user_state()
        user_state.conversation = conversation
        self.session_service.set_conversation_id(conversation.id)
        return user_state

    def on_conversation_created(self, conversation: Conversation) -> UserState:
        user_state = self.get_user_state()
        user_state.conversation = conversation
        self.session_service.set_conversation_id(conversation.id)
        return user_state
    
    def on_conversation_deleted(self, deleted_conversation_id: str) -> UserState:
        user_session = self.session_service.get_user_session()
        if (user_session.conversation_id == deleted_conversation_id):
            self.session_service.set_conversation_id(None)
        user_state = self.get_user_state()
        return user_state
    
    def on_conversation_rename(self, conversation: Conversation) -> UserState:
        user_state = self.get_user_state()
        user_state.conversation = conversation
        return user_state