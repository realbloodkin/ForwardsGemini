import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid, UserAlreadyParticipant

# --- Environment Variable ---
# Ensure this is set in your Koyeb service settings.
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")

# --- Constants for the interactive menu ---
OPTION_LABELS = ["Text", "Photos/Videos", "Audio", "Documents", "Stickers"]
# Default state: Only "Photos/Videos" and "Documents" are selected (original purpose)
DEFAULT_STATE = "01010" 

def create_selection_keyboard(selection_state: str, target_channel_id: str) -> InlineKeyboardMarkup:
    """Creates the interactive keyboard for selecting message types."""
    buttons = []
    state_list = list(selection_state)

    for i, label in enumerate(OPTION_LABELS):
        # Add a checkmark if the option is selected
        text = f"✅ {label}" if state_list[i] == '1' else label
        # The callback data encodes the action, current state, and the index to toggle
        callback_data = f"toggle_{selection_state}_{i}"
        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])
    
    # Action buttons
    buttons.append([
        InlineKeyboardButton("🚀 Start Scan", callback_data=f"start_{selection_state}_{target_channel_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_start(bot: Client, message: Message):
    """
    Initial entry point for the /unequify command.
    It validates input and presents the interactive selection menu.
    """
    if len(message.command) < 2:
        await message.reply_text(
            "**Please specify a target channel.**\n\n"
            "**Usage:** `/unequify [channel_username or chat_id]`"
        )
        return

    target_channel_input = message.command[1]

    if not USERBOT_SESSION_STRING:
        await message.reply_text("❌ **Configuration Error!**\n\nThe `USERBOT_SESSION_STRING` is not set.")
        return

    keyboard = create_selection_keyboard(DEFAULT_STATE, target_channel_input)
    await message.reply_text(
        "**Welcome to the Advanced Deduplicator!**\n\n"
        "Please select the types of messages you wish to find duplicates of. "
        "The original purpose (deleting duplicate files/media) is selected by default.",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex("^toggle_"))
async def toggle_selection(bot: Client, callback_query: CallbackQuery):
    """Handles clicks on the selection buttons to toggle their state."""
    _, current_state, index_str = callback_query.data.split("_")
    index = int(index_str)
    
    # The target channel ID is stored in the "Start" button's callback data
    start_button_data = callback_query.message.reply_markup.inline_keyboard[-1][0].callback_data
    target_channel_id = start_button_data.split("_")[-1]

    # Flip the bit at the specified index
    state_list = list(current_state)
    state_list[index] = '1' if state_list[index] == '0' else '0'
    new_state = "".join(state_list)

    # Update the keyboard with the new state
    new_keyboard = create_selection_keyboard(new_state, target_channel_id)
    await callback_query.message.edit_reply_markup(new_keyboard)
    await callback_query.answer() # Acknowledge the button press

@Client.on_callback_query(filters.regex("^cancel"))
async def cancel_operation(bot: Client, callback_query: CallbackQuery):
    """Handles the cancel button click."""
    await callback_query.message.edit_text("Operation cancelled.")

@Client.on_callback_query(filters.regex("^start_"))
async def start_deduplication(bot: Client, callback_query: CallbackQuery):
    """
    The main worker function, triggered after the user clicks "Start Scan".
    It performs the connection, permission checks, and deduplication logic.
    """
    status_message = callback_query.message
    await status_message.edit_text("`Processing your request...`", reply_markup=None)

    _, selection_state, target_channel_input = callback_query.data.split("_", 2)
    
    # Convert numeric chat IDs to integers
    try:
        if target_channel_input.startswith("-") and target_channel_input[1:].isdigit():
            target_channel = int(target_channel_input)
        else:
            target_channel = target_channel_input
    except ValueError:
        target_channel = target_channel_input

    selections = [OPTION_LABELS[i] for i, bit in enumerate(selection_state) if bit == '1']
    if not selections:
        await status_message.edit_text("❌ **No types selected!** Operation cancelled.")
        return

    await status_message.edit_text(f"`Initializing userbot session...\n\nTargeting: {', '.join(selections)}`")
    
    seen_identifiers = set()
    duplicates_to_delete = []
    total_scanned = 0
    total_deleted = 0

    try:
        async with Client(name="userbot_session", session_string=USERBOT_SESSION_STRING) as userbot:
            chat = None
            try:
                chat = await userbot.get_chat(target_channel)
            except (PeerIdInvalid, ChannelInvalid, UsernameNotOccupied):
                await status_message.edit_text("`Direct access failed. Attempting force-join to refresh session...`")
                await asyncio.sleep(2)
                try:
                    await userbot.join_chat(target_channel_input)
                    await asyncio.sleep(3)
                    chat = await userbot.get_chat(target_channel)
                except UserAlreadyParticipant:
                    await status_message.edit_text("`Already a member. Re-fetching chat data after refresh...`")
                    await asyncio.sleep(2)
                    chat = await userbot.get_chat(target_channel)
                except Exception as join_error:
                    await status_message.edit_text(f"❌ **Fatal Error!**\n\nFailed to access chat. Please check ID and permissions.\n\n`{join_error}`")
                    return
            
            if not chat:
                await status_message.edit_text("❌ **Fatal Error!** Could not retrieve chat object after all attempts.")
                return

            await status_message.edit_text(f"`Successfully accessed: {chat.title}`\n\n`Checking permissions...`")
            member = await userbot.get_chat_member(chat.id, "me")
            
            is_authorized = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            can_delete = member.privileges and member.privileges.can_delete_messages if member.privileges else False

            if not (is_authorized and (member.status == ChatMemberStatus.OWNER or can_delete)):
                await status_message.edit_text(f"❌ **Permission Denied in '{chat.title}'!** You must be an admin with delete rights or the owner.")
                return
            
            await status_message.edit_text(f"✅ **Permissions Confirmed!**\n\n`Starting scan...`")

            async for msg in userbot.get_chat_history(chat.id):
                total_scanned += 1
                identifier = None
                
                # Dynamic identifier based on user selection
                if selection_state[0] == '1' and msg.text:
                    identifier = msg.text.strip()
                elif selection_state[1] == '1' and (msg.photo or msg.video) and msg.media:
                    identifier = getattr(msg, msg.media.value).file_unique_id
                elif selection_state[2] == '1' and msg.audio:
                    identifier = msg.audio.file_unique_id
                elif selection_state[3] == '1' and msg.document:
                    identifier = msg.document.file_unique_id
                elif selection_state[4] == '1' and msg.sticker:
                    identifier = msg.sticker.file_unique_id

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
        await status_message.edit_text(f"❌ **An unexpected error occurred.**\n\n`{e}`")
