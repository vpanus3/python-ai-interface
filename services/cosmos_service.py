# pip install azure-cosmos
# db = "python-ai"
# container = "conversations" - partition by userId

import os
import json
from typing import List
from azure.cosmos import CosmosClient
from models.conversation import Conversation, UserConversation

ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["COSMOS_DB"]
CONVERSATIONS_CONTAINTER = os.environ["COSMOS_CONTIANER_CONVERSATIONS"]

class CosmosService:

    def __init__(self):
        self.client = CosmosClient(url=ENDPOINT, credential=KEY)
        self.database = self.client.get_database_client(DATABASE_NAME)
        self.conversations_container = self.database.get_container_client(CONVERSATIONS_CONTAINTER)

    def test(self):

        new_item = {
            "id": "70b63682-b93a-4c77-aad2-65501347265f",
            "user_id": "48f9f0e7-3312-425b-8281-4f72ab9a1419",
        }
        self.conversations_container.create_item(new_item)

        existing_item = self.container.read_item(
            item="70b63682-b93a-4c77-aad2-65501347265f",
            partition_key="48f9f0e7-3312-425b-8281-4f72ab9a1419"
        )

        return existing_item

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

