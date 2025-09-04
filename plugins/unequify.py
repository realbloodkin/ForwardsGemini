from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid
import os
import asyncio

# --- Environment Variable ---
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_deduplicate(bot: Client, message: Message):
    """
    Handles the /unequify command with a pre-scan chat discovery step
    to ensure the userbot session is aware of the target channel/group.
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
            
            # --- NEW: Chat Discovery Step ---
            # This forces the session to be aware of all chats, fixing CHANNEL_INVALID.
            await status_message.edit_text("`Synchronizing chat list... (Discovery Step)`")
            found_chat_in_dialogs = False
            try:
                async for dialog in userbot.get_dialogs():
                    if dialog.chat.id == target_channel:
                        found_chat_in_dialogs = True
                        break
                if not found_chat_in_dialogs:
                    await status_message.edit_text(f"❌ **Discovery Failed!**\n\nCould not find a chat with ID `{target_channel}` in my chat list. Please ensure I am a member.")
                    return
            except Exception as e:
                await status_message.edit_text(f"❌ **Error during Discovery:**\n`{e}`")
                return
            # --- END OF NEW STEP ---

            await status_message.edit_text(f"`Accessing chat: {target_channel_input}...`")
            chat = await userbot.get_chat(target_channel)

            await status_message.edit_text(f"`Found: {chat.title}`\n\n`Checking permissions...`")
            member = await userbot.get_chat_member(chat.id, "me")
            
            is_authorized = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            can_delete = member.privileges and member.privileges.can_delete_messages if member.privileges else False

            if not (is_authorized and (member.status == ChatMemberStatus.OWNER or can_delete)):
                await status_message.edit_text(
                    f"❌ **Permission Denied in '{chat.title}'!**\n\n"
                    "I am not an admin/owner with **'Delete Messages'** privilege."
                )
                return
            
            await status_message.edit_text(
                f"✅ **Permissions Confirmed!** (Status: `{member.status.name}`)\n\n`Starting scan...`"
            )
            await asyncio.sleep(2)

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
                
                if len(duplicates_to_delete) >= 100:
                    deleted_count = len(duplicates_to_delete)
                    await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                    total_deleted += deleted_count
                    duplicates_to_delete.clear()
                    await status_message.edit_text(
                        f"⚙️ **In progress...**\n"
                        f"Scanned: `{total_scanned}` | Deleted: `{total_deleted}`"
                    )
                    await asyncio.sleep(5)

            if duplicates_to_delete:
                deleted_count = len(duplicates_to_delete)
                await userbot.delete_messages(chat_id=chat.id, message_ids=duplicates_to_delete)
                total_deleted += deleted_count

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
