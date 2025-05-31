import os
from typing import Any
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import date

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["w"]
summaries_collection = db["summaries"]
personal_collection = db["personal"]

def save_summary(summary_data: str, date_obj: date):
    key = date_obj.strftime("%m-%d-%Y")

    summaries_collection.update_one(
        {"date": key},
        {"$set": {"content": summary_data}},
        upsert=True
    )

def get_summary(date_obj: date):
    key = date_obj.strftime("%m-%d-%Y")
    doc = summaries_collection.find_one({"date": key})
    return doc["content"] if doc and "content" in doc else None

def save_user_info(name: str, age: int, gender: str, about: str, category: str):
    personal_collection.update_one(
        {"key": "info"},
        {"$set": {
            "value": {
                "name": name,
                "age": age,
                "gender": gender,
                "about": about,
                "category": category
            }
        }},
        upsert=True
    )


def get_user_info() -> Any:
    doc = personal_collection.find_one({"key": "info"})
    return doc["value"] if doc and "value" in doc else None

def delete_all():
    personal_collection.delete_one({"key": "info"})
    summaries_collection.delete_many({})