import pymongo
import random
import string

client = pymongo.MongoClient("mongodb://localhost:30017")

db = client["loadtest"]
collection = db["data"]

while True:

    text = "".join(random.choices(string.ascii_letters, k=20000))

    doc = {
        "data": text
    }

    collection.insert_one(doc)

    print("Inserted document")