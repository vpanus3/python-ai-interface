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
    def from_chat_completion_response(cls, chat_completion):
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
    