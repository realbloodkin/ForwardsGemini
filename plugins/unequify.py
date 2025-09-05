import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid, UserAlreadyParticipant

# --- Environment Variable & In-Memory Storage ---
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")
# This dictionary will hold the user's progress through the conversation
user_context = {}

# --- Helper Functions for Keyboard Generation ---

def create_range_keyboard(chat_id, start_id=0, stop_id=0):
    """Creates the menu for setting the message ID range."""
    start_text = "Latest" if start_id == 0 else f"{start_id}"
    stop_text = "Oldest" if stop_id == 0 else f"{stop_id}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Scan Range: {start_text} ➡️ {stop_text}", callback_data="noop")],
        [
            InlineKeyboardButton("Set Start ID", callback_data=f"set_start_{chat_id}_{start_id}_{stop_id}"),
            InlineKeyboardButton("Set Stop ID", callback_data=f"set_stop_{chat_id}_{start_id}_{stop_id}")
        ],
        [InlineKeyboardButton("✅ Continue to Content Selection", callback_data=f"content_select_{chat_id}_{start_id}_{stop_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_full")]
    ])

def create_content_keyboard(chat_id, start_id, stop_id, selection_state="01010"):
    """Creates the menu for selecting content types to delete."""
    OPTION_LABELS = ["Text", "Photos/Videos", "Audio", "Documents", "Stickers"]
    buttons = []
    state_list = list(selection_state)
    for i, label in enumerate(OPTION_LABELS):
        text = f"✅ {label}" if state_list[i] == '1' else label
        callback_data = f"toggle_{selection_state}_{i}_{chat_id}_{start_id}_{stop_id}"
        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])
    
    buttons.append([
        InlineKeyboardButton("🚀 Start Scan", callback_data=f"start_{selection_state}_{chat_id}_{start_id}_{stop_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_full")
    ])
    return InlineKeyboardMarkup(buttons)


# --- Step 1: Initial Command ---

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_start(bot: Client, message: Message):
    """Starts the conversation, logs into the userbot, and lists available chats."""
    user_id = message.from_user.id
    if user_id in user_context:
        await message.reply_text("A previous operation is still in progress. Please cancel it first or wait for it to complete.")
        return

    status_message = await message.reply_text("`Initializing userbot session...`")

    if not USERBOT_SESSION_STRING:
        await status_message.edit_text("❌ **Configuration Error!** `USERBOT_SESSION_STRING` is not set.")
        return

    try:
        async with Client(name=f"userbot_session_{user_id}", session_string=USERBOT_SESSION_STRING) as userbot:
            await status_message.edit_text("`Fetching your chat list... This may take a moment.`")
            
            chat_list = []
            async for dialog in userbot.get_dialogs():
                if dialog.chat.type in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP]:
                    chat_list.append({"id": dialog.chat.id, "title": dialog.chat.title})
            
            if not chat_list:
                await status_message.edit_text("❌ **No channels or supergroups found** in the userbot's account.")
                return

            # Store chat list in context for the next step
            user_context[user_id] = {"step": "awaiting_chat_selection", "chats": chat_list}

            response_text = "**Select a Channel/Supergroup to Clean**\n\nReply with the corresponding number or the full Chat ID:\n\n"
            for i, chat in enumerate(chat_list, 1):
                response_text += f"**{i}.** `{chat['title']}`\n   (ID: `{chat['id']}`)\n"
            
            await status_message.edit_text(response_text, disable_web_page_preview=True)

    except Exception as e:
        await status_message.edit_text(f"❌ **An error occurred during userbot login:**\n`{e}`")
        if user_id in user_context:
            del user_context[user_id]


# --- Step 2: Handle User's Chat Selection & Other Text Inputs ---

@Client.on_message(filters.private & ~filters.command("start"))
async def handle_conversation(bot: Client, message: Message):
    """Manages text replies during the conversational setup."""
    user_id = message.from_user.id
    context = user_context.get(user_id)

    if not context:
        return

    # --- Awaiting Chat Selection ---
    if context.get("step") == "awaiting_chat_selection":
        try:
            selection = int(message.text)
            if 1 <= selection <= len(context["chats"]):
                # User selected by serial number
                chat_id = context["chats"][selection - 1]["id"]
            else:
                # User might have entered a chat ID directly
                chat_id = selection
        except ValueError:
            await message.reply_text("Invalid input. Please reply with a number or a valid Chat ID.")
            return

        user_context[user_id] = {"step": "awaiting_range_selection", "chat_id": chat_id}
        keyboard = create_range_keyboard(chat_id)
        await message.reply_text(f"Selected chat with ID: `{chat_id}`.\n\nNow, please configure the message scan range.", reply_markup=keyboard)

    # --- Awaiting Start/Stop Message ID ---
    elif context.get("step") in ["awaiting_start_id", "awaiting_stop_id"]:
        try:
            msg_id = int(message.text)
            if msg_id < 0: raise ValueError
        except ValueError:
            await message.reply_text("Invalid Message ID. Please enter a positive number.")
            return

        chat_id = context["chat_id"]
        start_id = context.get("start_id", 0)
        stop_id = context.get("stop_id", 0)

        if context["step"] == "awaiting_start_id":
            start_id = msg_id
        else:
            stop_id = msg_id
            
        user_context[user_id] = {"step": "awaiting_range_selection", "chat_id": chat_id, "start_id": start_id, "stop_id": stop_id}
        keyboard = create_range_keyboard(chat_id, start_id, stop_id)
        # Find the original message with the keyboard to edit it
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=context["status_message_id"],
            text=f"Selected chat with ID: `{chat_id}`.\n\nNow, please configure the message scan range.",
            reply_markup=keyboard
        )


# --- Step 3 & 4: Handle Button Clicks for Range and Content Selection ---

@Client.on_callback_query()
async def handle_callbacks(bot: Client, cq: CallbackQuery):
    """Handles all button clicks for the menus."""
    user_id = cq.from_user.id
    data = cq.data

    if data == "noop":
        await cq.answer()
        return

    if data == "cancel_full":
        if user_id in user_context:
            del user_context[user_id]
        await cq.message.edit_text("Operation cancelled.")
        return
        
    # --- Range Setting Callbacks ---
    if data.startswith("set_start_") or data.startswith("set_stop_"):
        _, step, chat_id_str, start_id_str, stop_id_str = data.split("_")
        user_context[user_id] = {
            "step": f"awaiting_{step}_id",
            "chat_id": int(chat_id_str),
            "start_id": int(start_id_str),
            "stop_id": int(stop_id_str),
            "status_message_id": cq.message.id # Store message_id to edit it later
        }
        prompt = "start" if step == "start" else "stop"
        await cq.message.reply_text(f"Please send the **{prompt} message ID**.", reply_markup=ForceReply(selective=True))
        await cq.answer()
        return

    # --- Move to Content Selection ---
    if data.startswith("content_select_"):
        _, chat_id_str, start_id_str, stop_id_str = data.split("_")
        keyboard = create_content_keyboard(chat_id_str, start_id_str, stop_id_str)
        await cq.message.edit_text(
            "**Select Content Types to Deduplicate**\n\nDefault is files/media.",
            reply_markup=keyboard
        )
        return

    # --- Toggle Content Types ---
    if data.startswith("toggle_"):
        _, state, index_str, chat_id_str, start_id_str, stop_id_str = data.split("_")
        index = int(index_str)
        state_list = list(state)
        state_list[index] = '1' if state_list[index] == '0' else '0'
        new_state = "".join(state_list)
        keyboard = create_content_keyboard(chat_id_str, start_id_str, stop_id_str, new_state)
        await cq.message.edit_reply_markup(keyboard)
        await cq.answer()
        return
        
    # --- Final Step: Start Scan ---
    if data.startswith("start_"):
        await start_deduplication(bot, cq)


# --- Final Step: The Main Worker Function ---

async def start_deduplication(bot: Client, cq: CallbackQuery):
    """The main worker function, triggered after all options are set."""
    user_id = cq.from_user.id
    status_message = cq.message
    await status_message.edit_text("`Finalizing settings...`", reply_markup=None)

    _, selection_state, chat_id_str, start_id_str, stop_id_str = cq.data.split("_", 4)
    target_channel_id = int(chat_id_str)
    start_message_id = int(start_id_str)
    stop_message_id = int(stop_id_str)
    
    selections = [OPTION_LABELS[i] for i, bit in enumerate(selection_state) if bit == '1']
    if not selections:
        await status_message.edit_text("❌ **No types selected!** Operation cancelled.")
        if user_id in user_context: del user_context[user_id]
        return

    await status_message.edit_text(f"`Initializing userbot session...\n\nTargeting: {', '.join(selections)}`")
    
    seen_identifiers = set()
    duplicates_to_delete = []
    total_scanned = 0
    total_deleted = 0

    try:
        async with Client(name=f"userbot_session_{user_id}", session_string=USERBOT_SESSION_STRING) as userbot:
            chat = await userbot.get_chat(target_channel_id)
            await status_message.edit_text(f"`Accessing: {chat.title}`\n\n`Checking permissions...`")
            member = await userbot.get_chat_member(chat.id, "me")
            
            if not (member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR] and (member.status == enums.ChatMemberStatus.OWNER or member.privileges.can_delete_messages)):
                await status_message.edit_text(f"❌ **Permission Denied in '{chat.title}'!**")
                return
            
            await status_message.edit_text(f"✅ **Permissions Confirmed!**\n\n`Starting scan...`")
            
            # Use offset_id to start from the specified message
            history_iterator = userbot.get_chat_history(chat.id, offset_id=start_message_id)

            async for msg in history_iterator:
                if stop_message_id != 0 and msg.id < stop_message_id:
                    break # Stop if we've reached the older message limit

                total_scanned += 1
                identifier = None
                
                # Dynamic identifier logic
                if selection_state[0] == '1' and msg.text: identifier = msg.text.strip()
                elif selection_state[1] == '1' and (msg.photo or msg.video) and msg.media: identifier = getattr(msg, msg.media.value).file_unique_id
                elif selection_state[2] == '1' and msg.audio: identifier = msg.audio.file_unique_id
                elif selection_state[3] == '1' and msg.document: identifier = msg.document.file_unique_id
                elif selection_state[4] == '1' and msg.sticker: identifier = msg.sticker.file_unique_id

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

    except Exception as e:
        await status_message.edit_text(f"❌ **An unexpected error occurred.**\n\n`{e}`")
    finally:
        if user_id in user_context:
            del user_context[user_id] # Clean up context after completion or failure
