# openai_service.py

import os
import openai
from typing import List, Callable
from models.openai_models import ChatRole, FinishReason, ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatState
from models.conversation_models import Conversation, ConversationMessage

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")
TEMPERATURE = float(os.getenv("OPENAI_Temperature"))
MAX_TOKENS = os.getenv("OPENAI_MaxTokens")

# Track ongoing chat states
CHAT_STATE = {}

class OpenAIService:

    def chat_is_streaming(self, conversation_id: str) -> bool:
        streaming = False
        state = CHAT_STATE.get(conversation_id, ChatState.NULL.value)
        if (state == ChatState.STREAMING.value): streaming = True
        return streaming

    def chat_is_cancelling(self, conversation_id: str) -> bool:
        streaming = False
        state = CHAT_STATE.get(conversation_id, ChatState.NULL.value)
        if (state == ChatState.CANCELLING.value): streaming = True
        return streaming
    
    def chat_set_state(self, conversation_id: str, streaming_state: ChatState):
        if (streaming_state is not None):
            CHAT_STATE[conversation_id] = streaming_state.value
        else: del CHAT_STATE[conversation_id]

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
            id = chat_completion_response.id,
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
        self.chat_set_state(conversation.id, ChatState.STREAMING)
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
        self.chat_set_state(conversation.id, ChatState.NULL)
        return conversation
    
    def stream_user_message(self, user_id: str, user_message: str, conversation: Conversation, stream_handler: Callable[[Conversation, bool], None]):
        
        chat_message = ChatMessage(ChatRole.USER, content=user_message)
        chat_request = self.get_chat_completion_request(
            chat_message=chat_message, 
            conversation=conversation,
            stream=True
        )
               
        messageCount = 0
        response_aggregate = None
        self.chat_set_state(conversation.id, ChatState.STREAMING)
        for chunk_completion in openai.ChatCompletion.create(
            model=chat_request.model,
            messages=chat_request.get_messages_dict(),
            temperature=chat_request.temperature,
            stream=chat_request.stream
        ):
            finished = False
            cancelling = self.chat_is_cancelling(conversation.id)
            messageCount = messageCount + 1
            response = ChatCompletionResponse.from_streaming_completion_chunk(chunk_completion)
            if (messageCount == 1):
                response_aggregate = response
                conversation = self.update_conversation(
                    user_id=user_id, 
                    chat_message=chat_message, 
                    conversation=conversation,
                    chat_completion_response = response_aggregate
                )
            else:
                message = next((msg for msg in conversation.messages if msg.id == response_aggregate.id))
                if message:
                    message.content = message.content + response.choices[0].message.content
                    message.finish_reason = response.choices[0].finish_reason
                    if (cancelling or message.finish_reason is not None): 
                        finished = True
                        self.chat_set_state(conversation.id, ChatState.NULL)
                else:
                    print("Message not found")

            stream_handler(conversation, finished)
            
            if (cancelling == True): break
        
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
