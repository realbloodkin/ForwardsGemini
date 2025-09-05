import os
import logging
import asyncio
import pyrogram
from pyrogram import Client, enums
from database import db 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# --- SECURE & FLEXIBLE CONFIGURATION ---
# These variables MUST be set in your Koyeb environment.
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_NAME = os.environ.get("BOT_NAME", "TestoDosBot") # Bot name can have a default
OWNER_ID = int(os.environ.get("OWNER_ID"))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL"))
# BOT_USERNAME and SUPPORT_GROUP have been removed as requested.

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=BOT_NAME,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=100,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )
        # This nested dictionary will hold the two persistent userbot clients.
        self.userbots = {}
        self.LOGGER = LOGGER

    async def start_userbots_from_storage(self):
        """Loads all persistent userbots from the database on bot startup."""
        self.LOGGER.info("Attempting to load persistent userbots from database...")
        all_users = await db.get_all_users()
        for user in all_users:
            user_id = user.get('id')
            if user_id not in self.userbots:
                self.userbots[user_id] = {}

            # 1. Load the "Settings Userbot" (from the main `bots` table)
            bot_data = await db.get_bot(user_id)
            if bot_data and bot_data.get('session'):
                try:
                    client = Client(name=f"userbot_db_{user_id}", session_string=bot_data['session'], in_memory=True)
                    await client.start()
                    self.userbots[user_id]['db'] = client
                    self.LOGGER.info(f"Successfully started 'Settings Userbot' for user {user_id}.")
                except Exception as e:
                    self.LOGGER.error(f"Failed to start 'Settings Userbot' for {user_id}: {e}")

            # 2. Load the "Command Userbot" (from the user `configs` table)
            configs = await db.get_configs(user_id)
            cmd_session = configs.get('command_userbot_session')
            if cmd_session:
                try:
                    client = Client(name=f"userbot_cmd_{user_id}", session_string=cmd_session, in_memory=True)
                    await client.start()
                    self.userbots[user_id]['cmd'] = client
                    self.LOGGER.info(f"Successfully started 'Command Userbot' for user {user_id}.")
                except Exception as e:
                    self.LOGGER.error(f"Failed to start 'Command Userbot' for {user_id}: {e}")

    async def start(self):
        await super().start()
        me = await self.get_me()
        # The bot's username is now fetched dynamically after starting up.
        self.username = me.username
        self.id = me.id
        self.log_channel = LOG_CHANNEL
        self.owner_id = OWNER_ID
        
        await self.start_userbots_from_storage()
        
        self.LOGGER.info(f"{me.first_name} with for Pyrogram v{pyrogram.__version__} (Layer {pyrogram.raw.all.layer}) started on @{me.username}.")
        self.LOGGER.info("Pyrogram v{pyrogram.__version__}")
        await self.send_message(
            chat_id=self.log_channel,
            text=f"**ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛᴇᴅ!**"
        )

    async def stop(self, *args):
        for user_id, bots in list(self.userbots.items()):
            for bot_type, client in list(bots.items()):
                if client.is_connected:
                    await client.stop()
                    self.LOGGER.info(f"Stopped '{bot_type}' userbot for user {user_id}.")
        await super().stop()
        self.LOGGER.info("Bot stopped. Bye.")

if __name__ == "__main__":
    app = Bot()
    app.run()
