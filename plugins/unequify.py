from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import asyncio

# --- Assumptions ---
# 1. 'userbot' is a Pyrogram Client instance that is initialized and started elsewhere in your code.
#    It might be a global variable or stored in a session dictionary. For this example, we'll assume it's accessible.
# 2. This file is a 'plugin' that gets loaded by your main bot.
#
# Replace the placeholder logic inside the 'try' block with your actual code.

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command(bot: Client, message: Message):
    """
    Handles the /unequify command to perform actions using the userbot.
    This version is modified for debugging a silent failure.
    """
    # Let's assume 'userbot' is accessible here. If it's stored differently,
    # you might need to fetch it (e.g., userbot = app.userbot_instance)
    global userbot # Or however you access your userbot client

    print("--- /unequify command triggered ---")
    await message.reply_text("Processing your request... Please wait.")

    # --- Step 1: Check if userbot is available ---
    if not userbot or not userbot.is_connected:
        print("DEBUG: FAILED - The userbot client is not available or not connected.")
        await message.reply_text("Error: Userbot is not available. Please add it first.")
        return

    print("DEBUG: SUCCESS - Userbot is available and connected.")

    try:
        processed_chats = []
        # --- Step 2: Your Core Logic Goes Here (Example: Iterating through chats) ---
        print("DEBUG: Attempting to get userbot's dialogs...")

        # Get all dialogs (chats) the userbot is in
        dialogs = userbot.get_dialogs()
        dialog_count = 0

        async for dialog in dialogs:
            dialog_count += 1
            print(f"DEBUG: Processing dialog #{dialog_count}: {dialog.chat.title or 'Unknown Title'} ({dialog.chat.id})")

            # --- Placeholder for your logic ---
            # Maybe you check for a specific condition before "unequifying"
            if "some_condition_to_check" in (dialog.chat.title or ""):
                print(f"DEBUG: Condition met for {dialog.chat.id}. Performing action.")
                # For example, leaving the chat
                # await userbot.leave_chat(dialog.chat.id)
                processed_chats.append(dialog.chat.title)
                # To avoid hitting API limits
                await asyncio.sleep(2)
            else:
                print(f"DEBUG: Condition NOT met for {dialog.chat.id}. Skipping.")
                pass
            # --- End of Placeholder ---

        print(f"DEBUG: Finished iterating through {dialog_count} dialogs.")

        # --- Step 3: Send the Final Report Message ---
        if not processed_chats:
            final_message = "Unequify process completed. No chats met the criteria to be processed."
            print(f"DEBUG: No chats were processed. Sending 'no action taken' message.")
        else:
            final_message = f"Unequify process completed successfully.\n\nProcessed Chats:\n- " + "\n- ".join(processed_chats)
            print(f"DEBUG: {len(processed_chats)} chats were processed. Sending success message.")

        await message.reply_text(final_message)
        print("--- /unequify command finished successfully ---")

    except FloodWait as fw:
        print(f"DEBUG: ERROR - Hit a FloodWait of {fw.value} seconds.")
        await asyncio.sleep(fw.value)
        await message.reply_text(f"FloodWait: Paused for {fw.value} seconds and will need to be restarted.")

    except Exception as e:
        # This is the most important part for debugging unexpected errors
        print(f"DEBUG: An unexpected ERROR occurred in the unequify command: {e}")
        # Also print the traceback for more details
        import traceback
        traceback.print_exc()
        await message.reply_text("An unexpected error occurred. Please check the logs for more details.")
