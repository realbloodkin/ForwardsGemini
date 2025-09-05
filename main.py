import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Minimal Configuration ---
# This uses only the three essential variables needed to connect.
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# We create the bot instance directly here for simplicity.
bot_app = Client("TestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot_app.on_message(filters.command("ping"))
async def ping(_, message: Message):
    """A simple command with no dependencies to test the core connection."""
    await message.reply_text("Pong! The core FastAPI + Pyrogram architecture is working.", quote=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On Startup
    print("--- MVB STARTUP ---")
    print("Starting minimal Pyrogram client...")
    await bot_app.start()
    print("Minimal Pyrogram client started successfully.")
    
    yield
    
    # On Shutdown
    print("--- MVB SHUTDOWN ---")
    print("Stopping minimal Pyrogram client...")
    await bot_app.stop()
    print("Minimal Pyrogram client stopped.")

# Initialize the FastAPI web app with the lifespan manager
web_app = FastAPI(lifespan=lifespan)

@web_app.get("/")
def read_root():
    return {"status": "Minimum Viable Bot is running"}
