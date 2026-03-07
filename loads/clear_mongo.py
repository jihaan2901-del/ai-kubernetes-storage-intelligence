import pymongo

client = pymongo.MongoClient("mongodb://localhost:30017")

db = client["loadtest"]

db.drop_collection("data")

print("MongoDB collection cleared")