# conversation.py

import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict
from models.openai_models import ChatRole, FinishReason, ChatMessage

@dataclass
class ConversationMessage:
    content: str = field(default='')
    role: ChatRole = field(default=None)
    created: int = field(default=None)
    model: str = field(default=None)
    temperature: int = field(default=None)
    finish_reason: FinishReason = field(default=None)

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.value if isinstance(o, Enum) else None)

    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'role': self.role.value if self.role else None,
            'created': self.created,
            'model': self.model,
            'temperature': self.temperature,
            'finish_reason': self.finish_reason.value if self.finish_reason else None
        }

    @classmethod
    def from_json(cls, json_str: str):
        message_dict = json.loads(json_str)
        if message_dict.get('role'):
            message_dict['role'] = ChatRole(message_dict['role'])
        if message_dict.get('finish_reason'):
            message_dict['finish_reason'] = FinishReason(message_dict['finish_reason'])
        return cls(**message_dict)
    
    @classmethod
    def from_dict(cls, message_dict: Dict):
        role = ChatRole(message_dict['role']) if message_dict.get('role') else None
        finish_reason = FinishReason(message_dict['finish_reason']) if message_dict.get('finish_reason') else None
        return cls(
            content=message_dict['content'],
            role=role,
            created=message_dict['created'],
            model=message_dict['model'],
            temperature=message_dict['temperature'],
            finish_reason=finish_reason
        )

@dataclass
class Conversation:
    id: str = field(default=str(uuid.uuid4()))
    user_id: str = field(default=None)
    title: str = field(default='')
    messages: List[ConversationMessage] = field(default_factory=list)

    def get_chat_messages(self) -> List[ChatMessage]:
        return [ChatMessage(message.role, message.content) for message in self.messages]

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.to_json() if isinstance(o, ConversationMessage) else None)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': [message.to_dict() for message in self.messages]
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_string: str):
        conversation_dict = json.loads(json_string)
        return cls.from_dict(conversation_dict)
    
    @classmethod
    def from_dict(cls, conversation_dict: Dict):
        messages = []
        if conversation_dict is not None:
            message_dicts = conversation_dict.get('messages', [])
            if message_dicts is not None and len(message_dicts) > 0:
                for message_dict in message_dicts:
                    message = ConversationMessage.from_dict(message_dict)
                    messages.append(message)
        return cls(
            id = conversation_dict.get('id', ''),
            user_id = conversation_dict.get('user_id', ''),
            title = conversation_dict.get('title', ''),
            messages = messages
        )

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
