import os
import threading
import asyncio
from flask import Flask
from bot import Bot # Your existing Bot class

# 1. Initialize the Flask web app for Render's health checks
web_app = Flask(__name__)

@web_app.route('/')
def hello_world():
    return 'Bot is alive and running!'

# 2. Initialize your Pyrogram Bot instance
bot_app = Bot()

# 3. Define the target function for the bot's thread
def run_bot():
    """
    This function will run in a separate thread.
    It creates and manages its own asyncio event loop.
    """
    # a. Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # b. Run the Pyrogram client's main coroutine within this loop
    # We use bot_app.start() and idle() for more control within a thread.
    loop.run_until_complete(bot_app.start())
    loop.run_forever() # Keeps the bot running until stopped

if __name__ == "__main__":
    # 4. Start the Pyrogram bot in its own background thread
    print("Starting bot thread...")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # 5. Run the Flask web app in the main thread
    # This part satisfies the Web Service requirement.
    print("Starting web server for health checks...")
    port = int(os.environ.get('PORT', 8080))
    web_app.run(host='0.0.0.0', port=port)
