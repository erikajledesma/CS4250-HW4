from pymongo import MongoClient

# create database connection object using pymongo

DB_NAME = "hw4"
DB_HOST = "localhost"
DB_PORT = 27017

try:
    client = MongoClient(host=DB_HOST, port=DB_PORT)
    db = client[DB_NAME]
    terms = db['terms']
    docs = db['documents']
except:
    print("Database not connected successfully")