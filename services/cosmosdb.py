# pip install azure-cosmos
# db = "python-ai"
# container = "conversations" - partition by userId

import os
import json
from azure.cosmos import CosmosClient, PartitionKey

ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["COSMOS_DB"]
CONVERSATIONS_CONTAINTER = os.environ["COSMOS_CONTIANER_CONVERSATIONS"]

class CosmosClientWrapper:

    def __init__(self):

        self.client = CosmosClient(url=ENDPOINT, credential=KEY)
        self.database = self.client.create_database_if_not_exists(id=DATABASE_NAME)
        key_path = PartitionKey(path="/userId")
        self.conversations_container = self.database.create_container_if_not_exists(
            id=CONVERSATIONS_CONTAINTER, partition_key=key_path, offer_throughput=400)

    def test(self):

        new_item = {
            "id": "70b63682-b93a-4c77-aad2-65501347265f",
            "userId": "48f9f0e7-3312-425b-8281-4f72ab9a1419",
        }
        self.conversations_container.create_item(new_item)

        existing_item = self.container.read_item(
            item="70b63682-b93a-4c77-aad2-65501347265f",
            partition_key="48f9f0e7-3312-425b-8281-4f72ab9a1419"
        )

        return existing_item

    def get_conversations_for_user(self, user_id: str):

        query = f"SELECT c.id, c.userId, c.title FROM c WHERE c.userId = '{user_id}'"
        items = list(self.conversations_container.query_items(query=query, enable_cross_partition_query=False))
    
    def get_conversation(self, user_id: str, conversation_id: str):

        query = f"SELECT * FROM c WHERE c.userId = '{user_id}' AND c.id ='{conversation_id}'"
        items = list(self.conversations_container.query_items(query=query, enable_cross_partition_query=False))



