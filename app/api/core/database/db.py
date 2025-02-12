from pymongo import MongoClient 
import os
from bson import ObjectId

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")  
client = MongoClient(MONGO_URL)
db = client["student_db"]
collection = db["students"]

def get_students():
    students = list(collection.find({}))  # Fetch all students including `_id`
    
    # Convert `_id` from ObjectId to string
    for student in students:
        student["_id"] = str(student["_id"])
    
    return students
