# pip install azure-cosmos
# db = "python-ai"
# container = "conversations" - partition by userId

import os
import json
from typing import List
from azure.cosmos import CosmosClient, PartitionKey
from models.conversation import Conversation, UserConversation

ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["COSMOS_DB"]
CONVERSATIONS_CONTAINTER = os.environ["COSMOS_CONTIANER_CONVERSATIONS"]

class CosmosService:

    def __init__(self):

        self.client = CosmosClient(url=ENDPOINT, credential=KEY)
        self.database = self.client.create_database_if_not_exists(id=DATABASE_NAME)
        key_path = PartitionKey(path="/user_id")
        self.conversations_container = self.database.create_container_if_not_exists(
            id=CONVERSATIONS_CONTAINTER, partition_key=key_path, offer_throughput=400)

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
        query = f"SELECT c.id, c.user_id, c.title FROM c WHERE c.user_id = '{user_id}'"
        items = list(self.conversations_container.query_items(query=query, enable_cross_partition_query=False))
        if items:
            for user_conversation_dict in items:
                user_conversation = UserConversation(user_conversation_dict.id, user_conversation_dict.user_id)
                user_conversations.append(user_conversation)
        return user_conversations
    
    def get_conversation(self, user_id: str, conversation_id: str) -> Conversation:
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}' AND c.id ='{conversation_id}'"
        items = list(self.conversations_container.query_items(query=query, enable_cross_partition_query=False))
        if items and len(items) == 1:
            conversation_json = json.dumps(items[0])
            conversation = Conversation.from_json(conversation_json)
        return conversation   

    def save_conversation(self, conversation: Conversation, user_id: str) -> Conversation:
        conversation
        conversation_dict = conversation.to_dict()
        conversation_dict = self.conversations_container.upsert_item(conversation_dict)

