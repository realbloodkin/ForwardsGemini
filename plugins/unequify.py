from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid
import os
import asyncio

# --- Environment Variable ---
# Ensure this is set in your Koyeb service settings.
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_deduplicate(bot: Client, message: Message):
    """
    Handles the /unequify command to find and delete duplicate messages
    (files, media, and text) within a single, specified channel.
    """
    # --- 1. Command and Input Validation ---
    status_message = await message.reply_text("`Processing your request...`")

    if len(message.command) < 2:
        await status_message.edit_text(
            "**Please specify a target channel.**\n\n"
            "**Usage:** `/unequify [channel_username or channel_id]`\n"
            "**Example:** `/unequify @mychannel` or `/unequify -100123456789`"
        )
        return

    target_channel = message.command[1]

    if not USERBOT_SESSION_STRING:
        await status_message.edit_text("❌ **Configuration Error!**\n\nThe `USERBOT_SESSION_STRING` is not set on the server.")
        return

    # --- 2. Initialize and Verify Userbot Session ---
    await status_message.edit_text("`Initializing userbot session...`")
    
    seen_identifiers = set()
    duplicates_to_delete = []
    total_scanned = 0
    total_found = 0

    try:
        print(f"DEBUG: Attempting to start userbot and target channel: {target_channel}")
        async with Client(name="userbot_session", session_string=USERBOT_SESSION_STRING) as userbot:
            await status_message.edit_text(f"`Accessing channel: {target_channel}...`")
            
            # Verify the channel exists and we can access it
            try:
                chat = await userbot.get_chat(target_channel)
            except (UsernameNotOccupied, UsernameInvalid, ChannelInvalid) as e:
                await status_message.edit_text(f"❌ **Error:** Could not find or access the channel '{target_channel}'. Please check the username/ID and ensure the userbot is a member.\n\n`{e}`")
                return

            await status_message.edit_text(
                f"✅ **Channel found:** {chat.title}\n\n"
                "`Starting scan for duplicates... This may take a while.`"
            )

            # --- 3. Scan History and Deduplicate ---
            async for msg in userbot.get_chat_history(chat.id):
                total_scanned += 1
                identifier = None

                # Create a unique identifier for each message type
                if msg.media and hasattr(msg, 'file_unique_id'):
                    identifier = msg.file_unique_id
                elif msg.text:
                    identifier = msg.text

                if identifier:
                    if identifier in seen_identifiers:
                        total_found += 1
                        duplicates_to_delete.append(msg.id)
                    else:
                        seen_identifiers.add(identifier)
                
                # Batch delete every 100 duplicates to be efficient
                if len(duplicates_to_delete) >= 100:
                    await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                    await status_message.edit_text(
                        f"⚙️ **In progress...**\n\n"
                        f"Scanned: `{total_scanned}` messages\n"
                        f"Deleted: `{total_found}` duplicates"
                    )
                    duplicates_to_delete.clear()
                    await asyncio.sleep(5) # Pause to respect API limits

            # Delete any remaining duplicates
            if duplicates_to_delete:
                await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)

            # --- 4. Final Report ---
            await status_message.edit_text(
                f"✅ **Deduplication Complete!**\n\n"
                f"**Channel:** {chat.title}\n"
                f"**Total Messages Scanned:** `{total_scanned}`\n"
                f"**Duplicate Messages Deleted:** `{total_found}`"
            )

    except FloodWait as e:
        await status_message.edit_text(f"❌ **Rate Limit Exceeded.**\n\nTelegram is limiting requests. Please wait `{e.value}` seconds before trying again.")
    except Exception as e:
        print(f"An unexpected ERROR occurred: {e}")
        import traceback
        traceback.print_exc()
        await status_message.edit_text(f"❌ **An unexpected error occurred.**\n\n`{e}`")
