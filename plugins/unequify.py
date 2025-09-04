from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid
import os
import asyncio

# --- Environment Variable ---
# Ensure this is set in your Koyeb service settings.
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_deduplicate(bot: Client, message: Message):
    """
    Handles the /unequify command to find and delete duplicate messages
    within a specified channel, with pre-scan permission checks.
    """
    # --- 1. Command and Input Validation ---
    status_message = await message.reply_text("`Processing your request...`")

    if len(message.command) < 2:
        await status_message.edit_text(
            "**Please specify a target channel.**\n\n"
            "**Usage:** `/unequify [channel_username or channel_id]`"
        )
        return

    target_channel_input = message.command[1]

    # FIX: Convert numeric chat IDs to integers to prevent PEER_ID_INVALID error
    try:
        if target_channel_input.startswith("-") and target_channel_input[1:].isdigit():
            target_channel = int(target_channel_input)
        else:
            target_channel = target_channel_input
    except ValueError:
        target_channel = target_channel_input

    if not USERBOT_SESSION_STRING:
        await status_message.edit_text("❌ **Configuration Error!**\n\nThe `USERBOT_SESSION_STRING` is not set.")
        return

    # --- 2. Initialize and Perform Permission Checks ---
    await status_message.edit_text("`Initializing userbot session...`")
    
    seen_identifiers = set()
    duplicates_to_delete = []
    total_scanned = 0
    total_deleted = 0

    try:
        async with Client(name="userbot_session", session_string=USERBOT_SESSION_STRING) as userbot:
            await status_message.edit_text(f"`Accessing channel: {target_channel_input}...`")
            
            try:
                chat = await userbot.get_chat(target_channel)
            except (PeerIdInvalid, UsernameNotOccupied, UsernameInvalid, ChannelInvalid) as e:
                await status_message.edit_text(f"❌ **Error:** Could not find '{target_channel_input}'. Please check the ID/username and ensure the userbot is a member.\n\n`{e}`")
                return

            # --- NEW: Pre-flight Permission Check ---
            await status_message.edit_text(f"`Found channel: {chat.title}`\n\n`Now, checking my permissions...`")
            member = await userbot.get_chat_member(chat.id, "me")
            
            can_delete = member.privileges and member.privileges.can_delete_messages
            
            if member.status != ChatMemberStatus.ADMINISTRATOR or not can_delete:
                await status_message.edit_text(
                    f"❌ **Permission Denied in '{chat.title}'!**\n\n"
                    "I am not an administrator or I lack the **'Delete Messages'** privilege.\n\n"
                    "Please promote my userbot account to an admin and grant this permission to proceed."
                )
                return
            
            await status_message.edit_text(
                f"✅ **Permissions Confirmed!**\n\n`Starting scan for duplicates in {chat.title}. This may take a while...`\n\n"
                "ℹ️ **Note:** As an admin, I can delete messages of any age. If I were a regular user, I could only delete messages newer than 48 hours."
            )
            await asyncio.sleep(3)

            # --- 3. Scan History and Deduplicate ---
            async for msg in userbot.get_chat_history(chat.id):
                total_scanned += 1
                identifier = None

                if msg.media and hasattr(msg.media, 'file_unique_id') and msg.media.file_unique_id:
                    identifier = msg.media.file_unique_id
                elif msg.text:
                    identifier = msg.text.strip()

                if identifier and identifier in seen_identifiers:
                    duplicates_to_delete.append(msg.id)
                elif identifier:
                    seen_identifiers.add(identifier)
                
                # Batch delete every 100 duplicates
                if len(duplicates_to_delete) >= 100:
                    deleted_count = len(duplicates_to_delete)
                    await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                    total_deleted += deleted_count
                    duplicates_to_delete.clear()
                    await status_message.edit_text(
                        f"⚙️ **In progress...**\n\n"
                        f"Scanned: `{total_scanned}` messages\n"
                        f"Deleted: `{total_deleted}` duplicates"
                    )
                    await asyncio.sleep(5)

            if duplicates_to_delete:
                deleted_count = len(duplicates_to_delete)
                await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                total_deleted += deleted_count

            # --- 4. Final Report ---
            await status_message.edit_text(
                f"✅ **Deduplication Complete!**\n\n"
                f"**Channel:** {chat.title}\n"
                f"**Total Messages Scanned:** `{total_scanned}`\n"
                f"**Duplicate Messages Deleted:** `{total_deleted}`"
            )

    except FloodWait as e:
        await status_message.edit_text(f"❌ **Rate Limit Exceeded.** Please wait `{e.value}` seconds before trying again.")
    except Exception as e:
        print(f"An unexpected ERROR occurred: {e}")
        import traceback
        traceback.print_exc()
        await status_message.edit_text(f"❌ **An unexpected error occurred.**\n\n`{e}`")
