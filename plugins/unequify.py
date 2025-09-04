from pyrogram import Client, filters
from pyrogram.types import Message
import os
import asyncio

# --- IMPORTANT ---
# You must have this environment variable set in your Koyeb service settings.
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_final(bot: Client, message: Message):
    """
    Handles the /unequify command by starting a temporary userbot client,
    performing the action, and then stopping it. This is the most reliable method.
    """
    # --- 1. Initial Setup and Pre-flight Checks ---
    status_message = await message.reply_text("✅ **Request received.**\n\nInitializing session...")

    if not USERBOT_SESSION_STRING:
        print("FATAL ERROR: USERBOT_SESSION_STRING is not set in environment variables.")
        await status_message.edit_text(
            "❌ **Configuration Error!**\n\n"
            "The `USERBOT_SESSION_STRING` is not set on the server. The command cannot proceed. "
            "Please contact the bot administrator."
        )
        return

    # --- 2. Start and Use the Userbot Client ---
    try:
        print("DEBUG: Initializing userbot from session string.")
        # The 'async with' block handles starting and stopping the client automatically
        async with Client(name="userbot_session", session_string=USERBOT_SESSION_STRING) as userbot:
            print("DEBUG: Userbot client started successfully.")
            user_details = userbot.me
            await status_message.edit_text(
                f"✅ **Userbot Active!**\n\n"
                f"Logged in as: **{user_details.first_name}** (`{user_details.id}`)\n\n"
                f"Starting to process chats..."
            )

            processed_count = 0
            dialog_count = 0

            # Iterate through dialogs one by one to avoid hanging
            async for dialog in userbot.get_dialogs():
                dialog_count += 1
                chat_title = dialog.chat.title or dialog.chat.first_name or "Unknown Chat"
                print(f"DEBUG: Processing dialog #{dialog_count}: {chat_title} ({dialog.chat.id})")

                # --- YOUR LOGIC GOES HERE ---
                # This is where you put your condition for what to "unequify".
                # For example, to leave any chat with "test channel" in the title:
                if "test channel" in chat_title.lower():
                    print(f"DEBUG: Condition MET for '{chat_title}'. Leaving chat.")
                    await userbot.leave_chat(dialog.chat.id)
                    processed_count += 1
                    await asyncio.sleep(2) # Prevent API flood limits
                # --- END OF YOUR LOGIC ---

                # Update the user every 50 scanned chats
                if dialog_count % 50 == 0:
                    await status_message.edit_text(
                        f"⚙️ **In progress...**\n\n"
                        f"Scanned: {dialog_count} chats\n"
                        f"Processed: {processed_count} chats"
                    )

            print("DEBUG: Finished iterating through all dialogs.")

            # --- 3. Final Report ---
            await status_message.edit_text(
                f"✅ **Process Complete!**\n\n"
                f"Total Chats Scanned: `{dialog_count}`\n"
                f"Total Chats Processed: `{processed_count}`"
            )

    except Exception as e:
        print(f"An unexpected ERROR occurred: {e}")
        import traceback
        traceback.print_exc()
        await status_message.edit_text(f"❌ **An error occurred.**\n\n`{e}`")
