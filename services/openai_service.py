# openai_service.py

import os
import openai
from typing import List
from models.openai_models import ChatRole, ChatMessage, ChatCompletionRequest, ChatCompletionResponse
from models.conversation_models import Conversation, ConversationMessage
from services.websocket_service import WebSocketService

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")
TEMPERATURE = float(os.getenv("OPENAI_Temperature"))
MAX_TOKENS = os.getenv("OPENAI_MaxTokens")

class OpenAIService:

    def __init__(self):
        self.websocket_service = WebSocketService()

    def get_chat_messages_from_conversation(self, conversation: Conversation) -> List[ChatMessage]:
        messages = []
        for history_message in conversation.messages:
            simple_message = ChatMessage(role=history_message.role, content=history_message.content
            )
            messages.append(simple_message)
        return messages

    def get_chat_completion_request(self, chat_message: ChatMessage, conversation: Conversation, stream: bool = False) -> ChatCompletionRequest:
        chat_messages = self.get_chat_messages_from_conversation(conversation)
        chat_messages.append(chat_message)
        request = ChatCompletionRequest(
            model= MODEL, 
            messages = chat_messages, 
            temperature = TEMPERATURE, 
            stream = stream)
        return request
    
    def update_conversation(self, user_id: str, chat_message: ChatMessage, conversation: Conversation, chat_completion_response: ChatCompletionResponse) -> Conversation:
        conversation = conversation or Conversation()
        conversation.user_id = conversation.user_id if conversation.user_id else user_id
        conversation.title = conversation.title if conversation.title else self.get_conversation_title(chat_message.content)

        conversation_message_request = ConversationMessage(
            content = chat_message.content,
            role = chat_message.role,
            created = chat_completion_response.created,
            model = chat_completion_response.model,
            temperature = TEMPERATURE,
            finish_reason= chat_completion_response.choices[0].finish_reason
        )
        conversation.messages.append(conversation_message_request)
        conversation_message_response = ConversationMessage(
            content = chat_completion_response.choices[0].message.content,
            role = chat_completion_response.choices[0].message.role,
            created = chat_completion_response.created,
            model = chat_completion_response.model,
            temperature = TEMPERATURE,
            finish_reason = chat_completion_response.choices[0].finish_reason
        )
        conversation.messages.append(conversation_message_response)
        return conversation
    
    def send_user_message(self, user_id: str, user_message: str, conversation: Conversation) -> Conversation:
        chat_message = ChatMessage(role=ChatRole.USER, content=user_message)
        chat_request = self.get_chat_completion_request(
            chat_message=chat_message, 
            conversation=conversation)
        response = openai.ChatCompletion.create(
            model=chat_request.model,
            messages=chat_request.get_messages_dict(),
            temperature=chat_request.temperature
        )
        chat_completion_response = ChatCompletionResponse.from_chat_completion_response(response)
        conversation = self.update_conversation(
            user_id=user_id, 
            chat_message=chat_message, 
            conversation=conversation,
            chat_completion_response= chat_completion_response)
        return conversation
    
    async def stream_user_message(self, user_id, str, user_message: str, conversation: Conversation):
        chat_message = ChatMessage(ChatRole.USER, content=user_message)
        chat_request = self.get_chat_completion_request(
            chat_message=chat_message, 
            conversation=conversation,
            stream=True
        )
        
        messageCount = 0
        response_aggregate = None
        self.websocket_service.start()
        for response in openai.ChatCompletion.create(
            model=chat_request.model,
            messages=chat_request.get_messages_dict(),
            temperature=chat_request.temperature,
            stream=chat_request.stream
        ):
            messageCount = messageCount + 1
            if (messageCount == 1):
                response_aggregate = ChatCompletionResponse.from_chat_completion_response(response)
            else:
                response_aggregate.choices[0].text = response_aggregate.choices[0].text + response.choices[0].text
            # send serializable object to websocket, async issues..
            await self.websocket_service.send_message(response_aggregate.to_dict())

        chat_completion_response = ChatCompletionResponse.from_chat_completion_response(response_aggregate)
        conversation = self.update_conversation(
            user_id=user_id, 
            chat_message=chat_message, 
            conversation=conversation,
            chat_completion_response= chat_completion_response)
        return conversation
    
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
