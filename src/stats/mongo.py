from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb://stats_mongo:27017/")
    return client.stats_db

