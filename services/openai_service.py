# openai_service.py

import os
import openai
from typing import List
from models.openai_models import ChatRole, ChatMessage, ChatCompletionRequest, ChatCompletionResponse
from models.conversation_models import Conversation, ConversationMessage
from services.websocket_service import WebSocketService

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getevn("OPENAI_MODEL")
TEMPERATURE = float(os.getenv("OPENAI_Temperature"))
MAX_TOKENS = os.getevn("OPENAI_MaxTokens")

class OpenAIService:

    def get_chat_messages_from_conversation(self, conversation: Conversation) -> List[ChatMessage]:
        messages = []
        for history_message in conversation.messages:
            simple_message = ChatMessage(history_message.role, history_message.content)
            messages.append(simple_message)
        return messages

    def get_chat_completion_request(self, chat_message: ChatMessage, converation: Conversation, stream: bool = False) -> ChatCompletionRequest:
        chat_messages = self.get_chat_messages_from_conversation(converation)
        chat_messages.append(chat_message)
        request = ChatCompletionRequest(MODEL, chat_messages, TEMPERATURE, stream)
        return request
    
    def update_converation(self, user_id: str, chat_message: ChatMessage, conversation: Conversation, chat_completion_response: ChatCompletionResponse) -> Conversation:
        conversation = conversation or Conversation()
        conversation.user_id = conversation.user_id if conversation.user_id else user_id
        conversation.title = conversation.title if conversation.title else self.get_conversation_title(chat_message.content)

        converation_message_request = ConversationMessage(
            chat_message.content,
            chat_message.role,
            chat_completion_response.created,
            chat_completion_response.model,
            TEMPERATURE,
            chat_completion_response.choices[0].finish_reason
        )
        conversation.messages.append(converation_message_request)
        converation_message_response = ConversationMessage(
            chat_completion_response.choices[0].message.content,
            chat_completion_response.choices[0].message.role,
            chat_completion_response.created,
            chat_completion_response.model,
            TEMPERATURE,
            chat_completion_response.choices[0].finish_reason
        )
        conversation.messages.append(converation_message_response)
        return conversation
    
    def send_user_message(self, user_id: str, user_message: str, conversation: Conversation) -> Conversation:
        chat_message = ChatMessage(ChatRole.USER, user_message)
        chat_request = self.get_chat_completion_request(
            chat_message=chat_message, 
            converation=conversation)
        response = openai.ChatCompletion.create(
            model=chat_request.model,
            messages=chat_request.get_messages_dict(),
            temperature=chat_request.temperature
        )
        chat_completion_response = ChatCompletionResponse.from_chat_completion_response(response)
        conversation = self.update_converation(
            user_id=user_id, 
            chat_message=chat_message, 
            conversation=conversation,
            chat_completion_response= chat_completion_response)
        return conversation
    
    def stream_user_message(self, user_id, str, user_message: str, conversation: Conversation):
        chat_message = ChatMessage(ChatRole.USER, user_message)
        chat_request = self.get_chat_completion_request(
            chat_message=chat_message, 
            converation=conversation,
            stream=True)
        response = openai.ChatCompletion.create(
            model=chat_request.model,
            messages=chat_request.get_messages_dict(),
            temperature=chat_request.temperature,
            stream=True
        )
        chat_completion_response = ChatCompletionResponse.from_chat_completion_response(response)
        conversation = self.update_converation(
            user_id=user_id, 
            chat_message=chat_message, 
            conversation=conversation,
            chat_completion_response= chat_completion_response)
    
    def get_conversation_title(self, user_message: str) -> str:
        prompt = (
            "Generate a title for the message of a conversation that is less than 50 characters long.\n"
            "\n"
            "Message: Tell me a robot joke.\n"
            "Title: Robot Joke\n"
            "Message: I want you to tell me how to be the best programmer ever!\n"
            "Title: Programming Tips\n"
            "Message: {}\n"
            "Title:"
        ).format(user_message)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.6,
        )
        return response.choices[0].text
