# pip install azure-cosmos
# db = "python-ai"
# container = "conversations" - partition by userId

import os
import json
from typing import List
from azure.cosmos import CosmosClient
from models.user_models import UserConversation
from models.conversation_models import Conversation

ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["COSMOS_DB"]
CONVERSATIONS_CONTAINTER = os.environ["COSMOS_CONTIANER_CONVERSATIONS"]

class ConversationService:

    def __init__(self):
        self.client = CosmosClient(url=ENDPOINT, credential=KEY)
        self.database = self.client.get_database_client(DATABASE_NAME)
        self.conversations_container = self.database.get_container_client(CONVERSATIONS_CONTAINTER)

    def get_user_conversations(self, user_id: str) -> List[UserConversation]:
        user_conversations = []
        query = f"SELECT c.id as conversation_id, c.user_id, c.title FROM c WHERE c.user_id = '{user_id}'"
        items = list(self.conversations_container.query_items(query=query, enable_cross_partition_query=False))
        if items:
            for user_conversation_dict in items:
                user_conversation = UserConversation.from_dict(user_conversation_dict)
                user_conversations.append(user_conversation)
        return user_conversations
    
    def get_conversation(self, user_id: str, conversation_id: str) -> Conversation | None:
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}' AND c.id ='{conversation_id}'"
        items = list(self.conversations_container.query_items(query=query, enable_cross_partition_query=False))
        if items and len(items) == 1:
            conversation_json = json.dumps(items[0])
            conversation = Conversation.from_json(conversation_json)
        return conversation   

    def save_conversation(self, conversation: Conversation) -> Conversation:
        conversation_dict = conversation.to_dict()
        conversation_dict = self.conversations_container.upsert_item(body=conversation_dict)
        return Conversation.from_dict(conversation_dict)
    
    def create_conversation(self, user_id: str) -> Conversation:
        conversation = Conversation(
            user_id=user_id
        )
        conversation = self.save_conversation(conversation)
        return conversation

