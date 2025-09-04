from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# Assuming 'userbot' is a global or otherwise accessible Pyrogram Client instance

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_robust(bot: Client, message: Message):
    """
    Handles the /unequify command robustly by streaming dialogs
    and providing progress updates to the user.
    """
    global userbot # Or your method for accessing the userbot

    # --- 1. Initial Setup and User Feedback ---
    status_message = await message.reply_text("✅ **Request received.**\n\nChecking userbot status...")
    print("--- /unequify command triggered ---")

    if not userbot or not userbot.is_connected:
        print("DEBUG: FAILED - Userbot is not available or not connected.")
        await status_message.edit_text("❌ **Error:** Userbot is not available. Please add and start it first.")
        return

    print("DEBUG: SUCCESS - Userbot is available.")
    await status_message.edit_text("✅ **Userbot is active.**\n\nStarting to process chats. This may take a while...")

    # --- 2. Process Dialogs as a Stream ---
    try:
        processed_count = 0
        dialog_count = 0
        processed_chats_titles = []

        # This is the key change: We use `async for` to process one chat at a time.
        # This prevents the bot from hanging while trying to load all chats at once.
        print("DEBUG: Starting to iterate through dialogs as a stream...")
        async for dialog in userbot.get_dialogs():
            dialog_count += 1
            chat_title = dialog.chat.title or dialog.chat.first_name or "Unknown Chat"
            print(f"DEBUG: Processing dialog #{dialog_count}: {chat_title} ({dialog.chat.id})")

            # --- YOUR LOGIC GOES HERE ---
            # Replace this `if` condition with your actual criteria for "unequifying"
            if "example" in chat_title.lower(): # Example: Leave chats with "example" in the title
                print(f"DEBUG: Condition MET for '{chat_title}'. Performing action.")
                # await userbot.leave_chat(dialog.chat.id) # Uncomment to perform the action
                processed_count += 1
                processed_chats_titles.append(chat_title)
                await asyncio.sleep(2) # Sleep to avoid API rate limits
            # --- END OF YOUR LOGIC ---

            # Provide a status update to the user every 25 chats
            if dialog_count % 25 == 0:
                await status_message.edit_text(
                    f"⚙️ **In progress...**\n\n"
                    f"Scanned: {dialog_count} chats\n"
                    f"Processed: {processed_count} chats"
                )

        print("DEBUG: Finished iterating through all dialogs.")

        # --- 3. Final Report ---
        final_report = (
            f"✅ **Unequify Process Completed!**\n\n"
            f"Total Chats Scanned: {dialog_count}\n"
            f"Total Chats Processed: {processed_count}\n\n"
        )
        if processed_chats_titles:
            final_report += "Affected Chats:\n- " + "\n- ".join(processed_chats_titles)

        await status_message.edit_text(final_report)

    except Exception as e:
        print(f"DEBUG: An unexpected ERROR occurred: {e}")
        import traceback
        traceback.print_exc()
        await status_message.edit_text(f"❌ **An unexpected error occurred.**\n\nError: `{e}`\n\nPlease check the logs for more details.")
