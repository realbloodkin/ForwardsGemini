import os
import threading
from flask import Flask
from bot import Bot # Your existing Bot class

# 1. Initialize the Flask web app
web_app = Flask(__name__)

@web_app.route('/')
def hello_world():
    # This is the endpoint Render will check to see if your service is alive
    return 'Bot is alive!'

# 2. Initialize your Pyrogram Bot
bot_app = Bot()

# 3. Define a function to run the bot
def run_bot():
    bot_app.run()

if __name__ == "__main__":
    # 4. Start the Pyrogram bot in a separate background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # 5. Run the Flask web app in the main thread
    # Gunicorn will listen on the port defined by the PORT environment variable.
    # The host '0.0.0.0' is important to make it accessible to Render.
    port = int(os.environ.get('PORT', 8080))
    web_app.run(host='0.0.0.0', port=port)
