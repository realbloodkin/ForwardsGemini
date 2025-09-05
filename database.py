import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

# --- THIS IS THE CRUCIAL FIX ---
# We now declare the client and collections as None at the module level.
# They will be initialized later, inside an async context.
motor_client = None
db = None
users_col = None
bots_col = None
channels_col = None
configs_col = None
# --- END OF THE FIX ---

async def init_database():
    """
    Initializes the database connection and performs a connection test.
    This function is now responsible for creating the client and collections.
    """
    global motor_client, db, users_col, bots_col, channels_col, configs_col

    MONGO_URI = os.environ.get("DATABASE_URI")
    if not MONGO_URI:
        print("FATAL ERROR: The 'DATABASE_URI' environment variable is not set.")
        sys.exit(1)
    
    print("--- DATABASE DIAGNOSTIC ---")
    print("SUCCESS: Found DATABASE_URI.")
    print("Attempting to connect to MongoDB...")

    try:
        motor_client = AsyncIOMotorClient(MONGO_URI)
        await motor_client.admin.command('ping')
        
        print("SUCCESS: MongoDB connection and authentication established.")
        
        # IMPORTANT: Replace 'forwardsgemini' with your actual database name.
        db_name = "forwardsgemini" 
        db = motor_client[db_name] 
        print(f"SUCCESS: Using database '{db.name}'.")
        print("--------------------------")

        # Initialize collections
        users_col = db['users']
        bots_col = db['bots']
        channels_col = db['channels']
        configs_col = db['configs']

    except ConnectionFailure as e:
        print("--- DATABASE DIAGNOSTIC ---")
        print("FATAL ERROR: Could not connect to the MongoDB server.")
        print("Please check your DATABASE_URI and MongoDB Atlas IP Access List (set to 0.0.0.0/0).")
        print(f"\nError Details: {e}")
        print("--------------------------")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected fatal error occurred during database initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# --- Your original database functions will now work correctly ---

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
