from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid, UserAlreadyParticipant
import os
import asyncio

# --- Environment Variable ---
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_deduplicate(bot: Client, message: Message):
    """
    Handles the /unequify command with a try-fail-refresh-retry mechanism
    to handle stubborn session synchronization issues like CHANNEL_INVALID.
    """
    status_message = await message.reply_text("`Processing your request...`")

    if len(message.command) < 2:
        await status_message.edit_text(
            "**Usage:** `/unequify [channel_username or chat_id]`"
        )
        return

    target_channel_input = message.command[1]
    try:
        if target_channel_input.startswith("-") and target_channel_input[1:].isdigit():
            target_channel = int(target_channel_input)
        else:
            target_channel = target_channel_input
    except ValueError:
        target_channel = target_channel_input

    if not USERBOT_SESSION_STRING:
        await status_message.edit_text("❌ **Configuration Error!** `USERBOT_SESSION_STRING` is not set.")
        return

    await status_message.edit_text("`Initializing userbot session...`")
    
    seen_identifiers = set()
    duplicates_to_delete = []
    total_scanned = 0
    total_deleted = 0

    try:
        async with Client(name="userbot_session", session_string=USERBOT_SESSION_STRING) as userbot:
            
            # --- NEW: Try-Fail-Refresh-Retry Logic ---
            chat = None
            try:
                await status_message.edit_text(f"`Attempting direct access to {target_channel_input}...`")
                chat = await userbot.get_chat(target_channel)
            except (PeerIdInvalid, ChannelInvalid, UsernameNotOccupied) as e:
                await status_message.edit_text(
                    f"`Direct access failed. Attempting force-join to refresh session...`\n\n"
                    f"This is a common fix for session sync issues."
                )
                await asyncio.sleep(2)
                try:
                    # Use the original string input for joining
                    await userbot.join_chat(target_channel_input)
                    await asyncio.sleep(3) # Give servers a moment to process the join
                    chat = await userbot.get_chat(target_channel) # Retry getting chat object
                except UserAlreadyParticipant:
                    # This is expected if the bot is already a member, we just needed to refresh.
                    # We still need to re-fetch the chat object after the "join" attempt.
                    await status_message.edit_text("`Already a member. Re-fetching chat data after refresh...`")
                    await asyncio.sleep(2)
                    chat = await userbot.get_chat(target_channel)
                except Exception as join_error:
                    await status_message.edit_text(
                        f"❌ **Fatal Error!**\n\nBoth direct access and the force-join refresh failed. I am unable to access this chat.\n\n"
                        f"**Please double-check the following:**\n"
                        f"1.  Is the Chat ID/Username `{target_channel_input}` absolutely correct?\n"
                        f"2.  Is the channel's privacy set in a way that might restrict API access?\n\n"
                        f"**Error:** `{join_error}`"
                    )
                    return
            # --- END OF NEW LOGIC ---

            if not chat:
                await status_message.edit_text("❌ **Fatal Error!** Could not retrieve chat object after all attempts.")
                return

            await status_message.edit_text(f"`Successfully accessed: {chat.title}`\n\n`Checking permissions...`")
            member = await userbot.get_chat_member(chat.id, "me")
            
            is_authorized = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            can_delete = member.privileges and member.privileges.can_delete_messages if member.privileges else False

            if not (is_authorized and (member.status == ChatMemberStatus.OWNER or can_delete)):
                await status_message.edit_text(f"❌ **Permission Denied in '{chat.title}'!**")
                return
            
            await status_message.edit_text(f"✅ **Permissions Confirmed!** (Status: `{member.status.name}`)\n\n`Starting scan...`")
            await asyncio.sleep(2)

            async for msg in userbot.get_chat_history(chat.id):
                total_scanned += 1
                # ... (rest of the deletion logic is the same) ...
                identifier = None
                if msg.media and hasattr(msg.media, 'file_unique_id') and msg.media.file_unique_id:
                    identifier = msg.media.file_unique_id
                elif msg.text:
                    identifier = msg.text.strip()
                if identifier and identifier in seen_identifiers:
                    duplicates_to_delete.append(msg.id)
                elif identifier:
                    seen_identifiers.add(identifier)
                if len(duplicates_to_delete) >= 100:
                    await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                    total_deleted += len(duplicates_to_delete)
                    duplicates_to_delete.clear()
                    await status_message.edit_text(f"⚙️ Scanned: `{total_scanned}` | Deleted: `{total_deleted}`")
                    await asyncio.sleep(5)
            if duplicates_to_delete:
                await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                total_deleted += len(duplicates_to_delete)

            await status_message.edit_text(
                f"✅ **Deduplication Complete!**\n\n"
                f"**Chat:** {chat.title}\n"
                f"**Messages Scanned:** `{total_scanned}`\n"
                f"**Duplicates Deleted:** `{total_deleted}`"
            )

    except FloodWait as e:
        await status_message.edit_text(f"❌ **Rate Limit Exceeded.** Please wait `{e.value}` seconds.")
    except Exception as e:
        print(f"An unexpected ERROR occurred: {e}")
        import traceback
        traceback.print_exc()
        await status_message.edit_text(f"❌ **An unexpected error occurred.**\n\n`{e}`")
