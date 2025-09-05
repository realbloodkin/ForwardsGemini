import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db 

# --- THIS IS THE FIX ---
# We get the OWNER_ID directly from the environment, just like in bot.py.
# This makes the file self-contained and resolves the NameError.
OWNER_ID = int(os.environ.get("OWNER_ID"))
# --- END OF THE FIX ---

@Client.on_message(filters.command("start") & filters.private)
async def start(bot: Client, message: Message):
    # This function is now correct and should respond.
    try:
        user_id = message.from_user.id
        is_new = await db.is_user_new(user_id)
        if is_new:
            await db.add_user(user_id, message.from_user.first_name)
        
        start_text = f"Hello {message.from_user.first_name}! I am your friendly bot."
        start_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ How to Use", callback_data="how_to_use")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about"), InlineKeyboardButton("📊 Status", callback_data="status")]
        ])
        
        await message.reply_text(
            text=start_text,
            reply_markup=start_buttons,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in /start command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply_text("Sorry, something went wrong. Please try again later.")

# --- THE FIX IS APPLIED HERE ---
@Client.on_message(filters.command("restart") & filters.user(OWNER_ID))
async def restart(bot: Client, message: Message):
    await message.reply_text("Restarting...")
    # This is a more robust way to handle restarts in a threaded environment
    os.execl(sys.executable, sys.executable, *sys.argv)

# --- The rest of your commands are preserved ---

@Client.on_message(filters.command("sydstart"))
async def sydstart(bot: Client, message: Message):
    await message.reply_text("Sydstart command received.")
    pass

@Client.on_callback_query(filters.regex("^helpcb$"))
async def helpcb(bot: Client, query):
    await query.message.edit_text("This is the help menu.")
    pass

@Client.on_callback_query(filters.regex("^how_to_use$"))
async def how_to_use(bot: Client, query):
    await query.message.edit_text("Here is how to use the bot...")
    pass

@Client.on_callback_query(filters.regex("^back$"))
async def back(bot: Client, query):
    # Assuming 'back' goes to the start menu
    start_text = f"Hello {query.from_user.first_name}! I am your friendly bot."
    start_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ How to Use", callback_data="how_to_use")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about"), InlineKeyboardButton("📊 Status", callback_data="status")]
    ])
    await query.message.edit_text(start_text, reply_markup=start_buttons)
    pass

@Client.on_callback_query(filters.regex("^about$"))
async def about(bot: Client, query):
    await query.message.edit_text("This bot was created to do awesome things.")
    pass

@Client.on_callback_query(filters.regex("^status$"))
async def status(bot: Client, query):
    total_users = await db.total_users_count()
    await query.answer(f"Total users in DB: {total_users}", show_alert=True)
    pass
