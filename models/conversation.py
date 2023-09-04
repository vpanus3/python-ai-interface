# conversation.py
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from models.openai_models import ChatRole, FinishReason, ChatMessage

@dataclass
class ConversationMessage:
    content: str
    role: ChatRole
    created: int
    model: str
    temperature: int
    finish_reason: FinishReason

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.value if isinstance(o, Enum) else None)

    def to_dict(self) -> dict:
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
    def from_dict(cls, message_dict):
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
    messages: List[ConversationMessage] = field(default_factory=list)

    def get_chat_messages(self) -> List[ChatMessage]:
        return [ChatMessage(message.role, message.content) for message in self.messages]

    def to_json(self):
        return json.dumps(self.to_dict(), default=lambda o: o.to_json() if isinstance(o, ConversationMessage) else None)

    def to_dict(self) -> dict:
        return {
            'messages': [message.to_dict() for message in self.messages]
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_string: str):
        conversation_dict = json.loads(json_string)
        return cls.from_dict(conversation_dict)
    
    @classmethod
    def from_dict(cls, conversation_dict: dict):
        messages = []
        message_dicts = conversation_dict.get('messages', [])
        
        for message_dict in message_dicts:
            message = ConversationMessage.from_dict(message_dict)  # Assuming you have a `from_dict` in ConversationMessage
            messages.append(message)

        return cls(messages=messages)