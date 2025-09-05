import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# --- THIS IS THE CRUCIAL FIX ---
# It now intelligently checks for the URI under multiple common names.
MONGO_URI = (
    os.environ.get("DATABASE_URI") or
    os.environ.get("DB_URL") or
    os.environ.get("MONGODB_URI")
)

if not MONGO_URI:
    print("FATAL ERROR: No database connection string found.")
    print("Please set DATABASE_URI in your environment variables.")
    sys.exit(1)

# We create one single, shared client instance when the bot starts.
try:
    motor_client = AsyncIOMotorClient(MONGO_URI)
    # IMPORTANT: Replace 'YourDatabaseName' with the actual name of your database.
    # If you don't have one, a good name is 'forwards_bot_db'.
    db = motor_client['YourDatabaseName'] 
    
    # Accessing the collections through the shared client
    users_col = db['users']
    bots_col = db['bots']
    channels_col = db['channels']
    configs_col = db['configs']
except Exception as e:
    print(f"FATAL ERROR: Could not connect to the MongoDB database.")
    print(f"Please check your DATABASE_URI and MongoDB Atlas IP Access List (set to 0.0.0.0/0).")
    print(f"Error details: {e}")
    sys.exit(1)
# --- END OF THE FIX ---


# --- RE-IMPLEMENTED DATABASE FUNCTIONS ---

async def is_user_new(user_id: int) -> bool:
    return await users_col.find_one({'id': user_id}) is None

async def add_user(user_id: int, first_name: str):
    await users_col.update_one({'id': user_id}, {'$set': {'name': first_name}}, upsert=True)

async def get_all_users():
    return users_col.find({})

async def total_users_count() -> int:
    return await users_col.count_documents({})

async def get_bot(user_id: int):
    return await bots_col.find_one({'id': user_id})

async def remove_bot(user_id: int):
    await bots_col.delete_one({'id': user_id})

async def get_configs(user_id: int):
    user_configs = await configs_col.find_one({'id': user_id})
    return user_configs or {}

async def update_configs(user_id: int, key: str, value):
    await configs_col.update_one({'id': user_id}, {'$set': {key: value}}, upsert=True)

async def get_user_channels(user_id: int):
    return channels_col.find({'user_id': user_id})

async def add_channel(user_id: int, chat_id: int, title: str, username: str):
    if await channels_col.find_one({'user_id': user_id, 'chat_id': str(chat_id)}):
        return False
    await channels_col.insert_one({'user_id': user_id, 'chat_id': str(chat_id), 'title': title, 'username': username})
    return True

async def remove_channel(user_id: int, chat_id: str):
    await channels_col.delete_one({'user_id': user_id, 'chat_id': chat_id})

async def get_channel_details(user_id: int, chat_id: str):
    return await channels_col.find_one({'user_id': user_id, 'chat_id': chat_id})

# Please re-implement any other custom database functions you have below,
# using the `users_col`, `bots_col`, etc. objects defined above.
