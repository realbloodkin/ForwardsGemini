import os
import logging
import time
import pyrogram
from pyrogram import Client, enums
from database import db # Assuming your database module is accessible

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# --- Your original configuration variables ---
# These will be read from your Koyeb environment.
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_NAME = os.environ.get("BOT_NAME", "TestoDosBot")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
OWNER_ID = int(os.environ.get("OWNER_ID"))
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL"))

class Bot(Client):
    def __init__(self):
        # --- Your original __init__ logic is preserved ---
        super().__init__(
            name=BOT_NAME,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=100,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )
        
        # --- INJECTION 1: Initialize the userbot dictionary ---
        # This creates the shared context for all plugins.
        self.userbots = {}
        
        # --- Your original logger attribute is preserved ---
        self.LOGGER = LOGGER

    # --- INJECTION 2: New helper function to load userbots from DB ---
    async def start_userbots_from_storage(self):
        """Loads all persistent userbots from both Settings (DB) and Commands (Configs)."""
        self.LOGGER.info("Attempting to load persistent userbots from database...")
        all_users = await db.get_all_users()
        for user in all_users:
            user_id = user.get('id')
            if user_id not in self.userbots:
                self.userbots[user_id] = {}

            # 1. Load the "Settings Userbot" (from main bots table)
            bot_data = await db.get_bot(user_id)
            if bot_data and bot_data.get('session'):
                try:
                    client = Client(name=f"userbot_db_{user_id}", session_string=bot_data['session'], in_memory=True)
                    await client.start()
                    self.userbots[user_id]['db'] = client
                    self.LOGGER.info(f"Successfully started 'Settings Userbot' for user {user_id}.")
                except Exception as e:
                    self.LOGGER.error(f"Failed to start 'Settings Userbot' for {user_id}: {e}")

            # 2. Load the "Command Userbot" (from user configs table)
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
        # --- Your original start logic is preserved ---
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.log_channel = LOG_CHANNEL
        self.owner_id = OWNER_ID
        
        # --- INJECTION 3: Call the new userbot loader function ---
        await self.start_userbots_from_storage()
        
        # --- Your original logging and messages are preserved ---
        self.LOGGER.info(f"{me.first_name} with for Pyrogram v{pyrogram.__version__} (Layer {pyrogram.raw.all.layer}) started on @{me.username}.")
        self.LOGGER.info("Pyrogram v{pyrogram.__version__}")
        await self.send_message(
            chat_id=self.log_channel,
            text=f"**ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛᴇᴅ!**"
        )

    async def stop(self, *args):
        # --- INJECTION 4: Gracefully stop all running userbots ---
        for user_id, bots in list(self.userbots.items()):
            for bot_type, client in list(bots.items()):
                if client.is_connected:
                    await client.stop()
                    self.LOGGER.info(f"Stopped '{bot_type}' userbot for user {user_id}.")

        # --- Your original stop logic is preserved ---
        await super().stop()
        self.LOGGER.info("Bot stopped. Bye.")

if __name__ == "__main__":
    app = Bot()
    app.run()
