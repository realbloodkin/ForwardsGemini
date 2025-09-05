import os
import threading
import asyncio
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Minimal Configuration ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 1. Initialize the Flask web app
web_app = Flask(__name__)
@web_app.route('/')
def hello_world():
    return 'Smoke Test Bot is alive!'

# 2. Initialize a minimal Pyrogram Bot
bot_app = Client("TestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot_app.on_message(filters.command("ping"))
async def ping(_, message: Message):
    await message.reply_text("Pong! The core connection is working.", quote=True)

# 3. Define the target function for the bot's thread
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_app.start())
    loop.run_forever()

if __name__ == "__main__":
    # 4. Start the Pyrogram bot in a separate background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # 5. Run the Flask web app in the main thread
    port = int(os.environ.get('PORT', 8080))
    web_app.run(host='0.0.0.0', port=port)
