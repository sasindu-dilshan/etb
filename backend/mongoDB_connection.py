import time
import pymongo
import certifi
from django.conf import settings

MONGO_URI = settings.MONGO_URI

connected = False
while not connected:
    try:
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        mongoDb = client['et']
        collection = mongoDb['et']
        print("Connected to MongoDB Atlas successfully!")
        connected = True
    except Exception as e:
        print("An error occurred while connecting to MongoDB Atlas:", e)
        print("Retrying in 1 second...")
        time.sleep(1)
