import json
from pymongo import MongoClient

# Function to read JSON data from a file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['user_data']
authorized_users_collection = db['authorized_users']

# Function to update or insert users into the database
def update_or_insert_users(users_data):
    for user in users_data:
        authorized_users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": user},
            upsert=True
        )
    return f"Updated or inserted {len(users_data)} users"

# Path to the JSON file
file_path = 'users_data.json'

# Read JSON data from the file
user_data = read_json_file(file_path)

# Format the data for MongoDB
formatted_data = [
    {
        "_id": user["_id"],
        "servers": user["servers"]
    }
    for user in user_data["authorized_users"]
]

# Update the database with the new data
result = update_or_insert_users(formatted_data)
print(result)
'''
all_users = db.authorized_users.find()
for user in all_users:
    print(user)
'''