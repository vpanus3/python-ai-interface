# openai_service.py

import os
import openai

from typing import List, Dict, Optional
from models.openai_models import ChatRole, ChatMessage, ChatCompletionRequest, ChatCompletionResponse
from models.conversation import Conversation, ConversationMessage

openai.api_key = os.getenv("OPENAI_API_KEY")
TEMPERATURE = float(os.getenv("OPENAI_Temperature"))

class OpenAIService:

    def get_chat_messages_from_conversation(self, conversation: Conversation) -> List[ChatMessage]:
        messages = []
        for history_message in conversation.messages:
            simple_message = ChatMessage(history_message.role, history_message.content)
            messages.append(simple_message)
        return messages

    def get_chat_completion_request(self, chat_message: ChatMessage, converation: Conversation) -> ChatCompletionRequest:
        chat_messages = self.get_chat_messages_from_conversation(converation)
        chat_messages.append(chat_message)
        request = ChatCompletionRequest('gpt-3.5-turbo-0613', chat_messages, TEMPERATURE)
        return request

    def update_converation(self, converation: Conversation, chat_message: ChatMessage, chat_completion_response: ChatCompletionResponse) -> Conversation:
        converation = converation or Conversation()
        converation_message_request = ConversationMessage(
            chat_message.content,
            chat_message.role,
            chat_completion_response.created,
            chat_completion_response.model,
            TEMPERATURE,
            chat_completion_response.choices[0].finish_reason
        )
        converation.messages.append(converation_message_request)
        converation_message_response = ConversationMessage(
            chat_completion_response.choices[0].message.content,
            chat_completion_response.choices[0].message.role,
            chat_completion_response.created,
            chat_completion_response.model,
            TEMPERATURE,
            chat_completion_response.choices[0].finish_reason
        )
        converation.messages.append(converation_message_response)
        return converation
    
    def send_user_message(self, user_message: str, conversation: Conversation) -> Conversation:
        chat_message = ChatMessage(ChatRole.USER, user_message)
        chat_request = self.get_chat_completion_request(chat_message, conversation)
        response = openai.ChatCompletion.create(
            model=chat_request.model,
            messages=chat_request.get_messages_dict(),
            temperature=chat_request.temperature,
        )
        chat_completion_response = ChatCompletionResponse.from_chat_completion_response(response)
        conversation = self.update_converation(conversation, chat_message, chat_completion_response)
        return conversation
