# conversation.py

from enum import Enum
from typing import List, Dict, Optional
from models.openai_models import ChatRole, FinishReason, ChatMessage

class ConversationMessage:

    def __init__(self, content: str, role: ChatRole, created: int, model: str, temperature: int, finish_reason: FinishReason):
        self.content = content
        self.role = role
        self.created = created
        self.model = model
        self.temperature = temperature
        self.finish_reason = finish_reason

    def to_dict(self) -> dict:
        return {
            'content': self.content,
            'role': self.role.value if self.role else None,  # Convert enum to string
            'created': self.created,
            'model': self.model,
            'temperature': self.temperature,
            'finish_reason': self.finish_reason.value if self.finish_reason else None  # Convert enum to string
        }
    
    @classmethod
    def from_dict(cls, message_dict: dict):
        role = ChatRole(message_dict['role']) if message_dict['role'] else None
        finish_reason = FinishReason(message_dict['finish_reason']) if message_dict['finish_reason'] else None
        return ConversationMessage(
            content=message_dict['content'],
            role=role,
            created=message_dict['created'],
            model=message_dict['model'],
            temperature=message_dict['temperature'],
            finish_reason=finish_reason
        )

class Conversation:

    def __init__(self, messages: Optional[List[ConversationMessage]] = None):
        self.messages = messages or []
    

    def get_chat_messages(self) -> List[ChatMessage]:
        messages = []
        for history_message in self.messages:
            simple_message = ChatMessage(history_message.role, history_message.content)
            messages.append(simple_message)
        return messages
    
    def to_dict(self):
        return {
            'messages': [message.to_dict() for message in self.messages]
        }
    
    @classmethod
    def from_dict(cls, chat_history_dict: dict):
        messages = []
        messages_dict = chat_history_dict.get('messages', [])
        for message in messages_dict:
            chat_history_message = ConversationMessage.from_dict(message)
            messages.append(chat_history_message)        
        return cls(messages=messages)