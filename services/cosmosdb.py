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

    def test(self):
        new_item = {
            "id": "70b63682-b93a-4c77-aad2-65501347265f",
            "categoryId": "61dba35b-4f02-45c5-b648-c6badc0cbd79",
            "categoryName": "gear-surf-surfboards",
            "name": "Yamba Surfboard",
            "quantity": 12,
            "sale": False,
        }

