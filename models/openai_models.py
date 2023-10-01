# openai.py

from enum import Enum
import uuid
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

    def __init__(self, model: str, messages: List[ChatMessage], temperature: float, stream:bool = False):
        self.model = model
        self.messages = messages or []
        self.temperature = temperature
        self.stream = stream

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
    def from_chat_completion_response(cls, chat_completion):
        choices = []
        if chat_completion and len(chat_completion.choices) > 0:
            choice = chat_completion.choices[0]
            chat_message = ChatMessage(ChatRole(choice.message.role), choice.message.content)
            chat_choice = ChatChoice(choice.index, chat_message, FinishReason(choice.finish_reason))
            choices.append(chat_choice)

        return ChatCompletionResponse(
            id = chat_completion.id,
            object = chat_completion.object,
            created = chat_completion.created,
            model = chat_completion.model,
            choices = choices,
            usage = chat_completion.usage
        )
    
    @classmethod
    def from_streaming_completion_chunk(cls, chunk_completion):
        choices = []
        if chunk_completion and len(chunk_completion.choices) > 0:
            choice = chunk_completion.choices[0]
            role = ChatRole.ASSISTANT
            content = ''
            if choice.get('delta') and choice['delta'].get('role') is not None:
                role = ChatRole(choice.delta.role)
            if choice.get('delta') and choice['delta'].get('content') is not None:
                content = choice.delta.content
            chat_message = ChatMessage(role, content)
            chat_choice = ChatChoice(choice.index, chat_message, FinishReason(choice.finish_reason))
            choices.append(chat_choice)

        return ChatCompletionResponse(
            id = chunk_completion.id,
            object = chunk_completion.object,
            created = chunk_completion.created,
            model = chunk_completion.model,
            choices = choices,
            usage = ''
        )
    