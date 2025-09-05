import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot import Bot # Your existing Bot class from bot.py

# This special "lifespan" function is the core of the solution.
# It tells FastAPI what to do on startup and shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- On Startup ---
    print("Web server is starting up...")
    # Initialize your Pyrogram Bot
    bot_app = Bot()
    # Start the bot. It will run in the same event loop as the web server.
    await bot_app.start()
    print("Pyrogram bot has started successfully.")
    
    yield # The web server runs here
    
    # --- On Shutdown ---
    print("Web server is shutting down...")
    # Gracefully stop the bot.
    await bot_app.stop()
    print("Pyrogram bot has stopped.")

# Initialize the FastAPI web app with our new lifespan manager
web_app = FastAPI(lifespan=lifespan)

@web_app.get("/")
def read_root():
    # This is the endpoint Render will check to see if your service is alive.
    return {"status": "Bot is running"}
