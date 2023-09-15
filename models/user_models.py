# user.py

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict
from models.conversation_models import Conversation

@dataclass
class UserConversation:
    conversation_id: str = field(default=None)
    user_id: str = field(default=None)
    title: str = field(default=None)

    def to_dict(self):
        return {
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'title': self.title
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str):
        data_dict = json.loads(json_str)
        return cls.from_dict(data_dict)

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(
            conversation_id=data_dict.get('conversation_id', ''),
            user_id=data_dict.get('user_id', ''),
            title=data_dict.get('title', '')
        )

@dataclass
class UserSession:
    user_id: str = field(default=None)
    user_conversations: List[UserConversation] = field(default_factory=list)
    conversation: Conversation = field(default=None)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_conversations': [user_conversation.to_dict() for user_conversation in self.user_conversations],
            'conversation': self.conversation.to_dict() if self.conversation is not None else None
        }

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.value if isinstance(o, Enum) else None)

    @classmethod
    def from_dict(cls, data_dict: dict):
        user_conversations = [UserConversation.from_dict(conv_dict) for conv_dict in data_dict.get('user_conversations', [])]
        conversation = Conversation.from_dict(data_dict.get('conversation', {}))
        return cls(
            user_id=data_dict.get('user_id', ''),
            user_conversations=user_conversations,
            conversation=conversation
        )

    @classmethod
    def from_json(cls, json_str: str):
        data_dict = json.loads(json_str)
        return cls.from_dict(data_dict)