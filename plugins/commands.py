import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db # Assuming your database module is named 'db'

# --- The /start Command with Full Diagnostics ---

@Client.on_message(filters.command("start") & filters.private)
async def start(bot: Client, message: Message):
    # INJECTION: Confirm the function is being triggered in your logs
    print(f"[DEBUG] /start command triggered by user {message.from_user.id}")

    try:
        user_id = message.from_user.id
        
        # This is a common pattern: check if user is in the database.
        # Replace 'is_user_new' and 'add_user' with your actual function names if different.
        is_new = await db.is_user_new(user_id)

        # INJECTION: Check the result of the database call
        print(f"[DEBUG] Database check complete. Is new user? {is_new}")

        if is_new:
            print("[DEBUG] Adding new user to database...")
            await db.add_user(user_id, message.from_user.first_name)
            print("[DEBUG] New user added successfully.")
        
        # --- YOUR ORIGINAL START MESSAGE LOGIC GOES HERE ---
        # This is where your code to prepare the buttons and text would be.
        # I have added a plausible example based on your bot's other commands.
        start_text = f"Hello {message.from_user.first_name}! I am your friendly bot."
        
        start_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ How to Use", callback_data="how_to_use")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about"), InlineKeyboardButton("📊 Status", callback_data="status")]
        ])
        
        # INJECTION: Confirm the bot is about to send a reply
        print(f"[DEBUG] About to send start message reply to {user_id}.")
        
        await message.reply_text(
            text=start_text,
            reply_markup=start_buttons,
            disable_web_page_preview=True
        )
        
        print("[DEBUG] /start command finished successfully.")

    except Exception as e:
        # --- INJECTION: This will catch ANY hidden errors ---
        print("!!!!!!!!!!!!!!! AN ERROR OCCURRED IN /START !!!!!!!!!!!!!!!")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception details: {e}")
        import traceback
        traceback.print_exc() # This will print the full error traceback to your log
        # --- END OF INJECTION ---
        # Optionally, inform the user that something went wrong.
        await message.reply_text("Sorry, something went wrong. Please try again later.")

# --- Placeholders for Your Other Commands (to preserve functionality) ---

@Client.on_message(filters.command("restart") & filters.user(bot.owner_id)) # Assuming OWNER_ID is on the bot client
async def restart(bot: Client, message: Message):
    # Your original restart logic
    await message.reply_text("Restarting...")
    os.execl(sys.executable, sys.executable, "-m", "bot") # Example restart logic

@Client.on_message(filters.command("sydstart"))
async def sydstart(bot: Client, message: Message):
    # Your original sydstart logic
    await message.reply_text("Sydstart command received.")
    pass

@Client.on_callback_query(filters.regex("^helpcb$"))
async def helpcb(bot: Client, query):
    # Your original help callback logic
    await query.message.edit_text("This is the help menu.")
    pass

@Client.on_callback_query(filters.regex("^how_to_use$"))
async def how_to_use(bot: Client, query):
    # Your original how_to_use logic
    await query.message.edit_text("Here is how to use the bot...")
    pass

@Client.on_callback_query(filters.regex("^back$"))
async def back(bot: Client, query):
    # Your original back button logic
    # This might go back to the start menu
    await query.message.edit_text("Going back...")
    pass

@Client.on_callback_query(filters.regex("^about$"))
async def about(bot: Client, query):
    # Your original about logic
    await query.message.edit_text("This bot was created to do awesome things.")
    pass

@Client.on_callback_query(filters.regex("^status$"))
async def status(bot: Client, query):
    # Your original status logic
    total_users = await db.total_users_count() # Example db function
    await query.answer(f"Total users in DB: {total_users}", show_alert=True)
    pass
