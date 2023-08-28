# openai.py

from enum import Enum
from typing import List, Dict, Optional

class ChatRole(Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class FinishReason(Enum):
    STOP = 'stop'
    LENGTH = 'length'
    FUNCTION_CALL = 'function_call'
    CONTENT_FILTER = 'content_filter'
    NULL = None

class ChatMessage:
    
    def __init__(self, role: ChatRole, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict:
        return {
            'role': self.role.value,
            'content': self.content
        }

class ChatCompletionRequest:

    def __init__(self, model: str, messages: List[ChatMessage], temperature: float):
        self.model = model
        self.messages = messages or []
        self.temperature = temperature

    def get_messages_dict(self) -> Dict:
        return [message.to_dict() for message in self.messages]

class ChatChoice:

    def __init__(self, index: int, message: ChatMessage, finish_reason: FinishReason):
        self.index = index
        self.message = message
        self.finish_reason = finish_reason

class ChatUsage:

    def __init__(self, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

class ChatCompletionResponse:

    def __init__(self, id: str, object: str, created: int, model: str, choices: List[ChatChoice], usage: ChatUsage):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices or []
        self.usage = usage

    @classmethod
    def from_chat_completion(cls, chat_completion):
        choices = []
        if chat_completion and len(chat_completion.choices) > 0:
            choice = chat_completion.choices[0]
            chat_message = ChatMessage(ChatRole(choice.message.role), choice.message.content)
            chat_choice = ChatChoice(choice.index, chat_message, FinishReason(choice.finish_reason))
            choices.append(chat_choice)

        return ChatCompletionResponse(
            chat_completion.id,
            chat_completion.object,
            chat_completion.created,
            chat_completion.model,
            choices,
            chat_completion.usage
        )

class ChatHistoryMessage:

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
        return ChatHistoryMessage(
            content=message_dict['content'],
            role=role,
            created=message_dict['created'],
            model=message_dict['model'],
            temperature=message_dict['temperature'],
            finish_reason=finish_reason
        )

class ChatHistory:

    def __init__(self, messages: Optional[List[ChatHistoryMessage]] = None):
        self.messages = messages or []
    
    def append_user_message(self, message: str):
        chat_message = ChatMessage(ChatRole.USER, message)
        self.messages.append(chat_message)

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
            chat_history_message = ChatHistoryMessage.from_dict(message)
            messages.append(chat_history_message)        
        return cls(messages=messages)