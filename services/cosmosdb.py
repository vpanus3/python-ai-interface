# pip install azure-cosmos
#  
# db = "python-ai"
# container = "conversations" - partition by userId

# CosmosClient client = new CosmosClient(
#    "https://localhost:8081", 
#     "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==");

import os
import json
from azure.cosmos import CosmosClient, PartitionKey

ENDPOINT = os.environ["COSMOS_ENDPOINT"]
KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["COSMOS_DB"]
CONTAINER_NAME = os.environ["COSMOS_CONTIANER_CONVERSATIONS"]

class CosmosClientWrapper:

    def __init__(self):

        self.client = CosmosClient(url=ENDPOINT, credential=KEY)
        self.database = self.client.create_database_if_not_exists(id=DATABASE_NAME)
        key_path = PartitionKey(path="/userId")
        self.container = self.database.create_container_if_not_exists(
            id=CONTAINER_NAME, partition_key=key_path, offer_throughput=400)

    def test(self):

        new_item = {
            "id": "70b63682-b93a-4c77-aad2-65501347265f",
            "userId": "48f9f0e7-3312-425b-8281-4f72ab9a1419",
        }
        self.container.create_item(new_item)

        existing_item = self.container.read_item(
            item="70b63682-b93a-4c77-aad2-65501347265f",
            partition_key="48f9f0e7-3312-425b-8281-4f72ab9a1419"
        )

        print("Point read\t", existing_item["name"])



