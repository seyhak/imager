import os

from dotenv import load_dotenv
from pymongo import MongoClient


def get_mongo_db_client():
    load_dotenv()
    MONGO_HOST = os.environ.get("MONGO_HOST")
    MONGO_PORT = os.environ.get("MONGO_PORT")
    MONGO_USER = os.environ.get("MONGO_USER")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")

    client = MongoClient(
        host=MONGO_HOST,
        port=int(MONGO_PORT),
        username=MONGO_USER,
        password=MONGO_PASSWORD,
    )
    return client
