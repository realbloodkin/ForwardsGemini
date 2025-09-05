import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply
from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied, UsernameInvalid, PeerIdInvalid, UserAlreadyParticipant

# --- Environment Variable & In-Memory Storage ---
USERBOT_SESSION_STRING = os.environ.get("USERBOT_SESSION_STRING")
# This dictionary will hold the user's progress through the conversation
user_context = {}

# --- Constants & Keyboards ---
OPTION_LABELS = ["Text", "Photos/Videos", "Audio", "Documents", "Stickers"]

def create_range_keyboard(chat_id, start_id=0, stop_id=0):
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
    user_id = message.from_user.id
    if user_id in user_context:
        await message.reply_text("A previous operation is still in progress. Please use /cancel or wait for it to complete.")
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
                await status_message.edit_text("❌ **No channels or supergroups found**.")
                return

            user_context[user_id] = {"step": "awaiting_chat_selection", "chats": chat_list}
            response_text = "**Select a Channel/Supergroup**\n\nReply with the number or the full Chat ID:\n\n"
            for i, chat in enumerate(chat_list, 1):
                response_text += f"**{i}.** `{chat['title']}`\n   (ID: `{chat['id']}`)\n"
            await status_message.edit_text(response_text, disable_web_page_preview=True)
    except Exception as e:
        await status_message.edit_text(f"❌ **Userbot Login Error:**\n`{e}`")
        if user_id in user_context: del user_context[user_id]

# --- Step 2: Handle User's Text Replies ---

@Client.on_message(filters.private & filters.reply & ~filters.command("unequify"))
async def handle_text_replies(bot: Client, message: Message):
    user_id = message.from_user.id
    context = user_context.get(user_id)
    if not context or not message.reply_to_message: return

    # --- Awaiting Start/Stop Message ID ---
    if context.get("step") in ["awaiting_start_id", "awaiting_stop_id"]:
        try:
            msg_id = int(message.text)
            if msg_id <= 0: raise ValueError
        except (ValueError, TypeError):
            await message.reply_text("Invalid Message ID. Please enter a positive number.")
            return

        chat_id = context["chat_id"]
        start_id = context.get("start_id", 0)
        stop_id = context.get("stop_id", 0)

        if context["step"] == "awaiting_start_id": start_id = msg_id
        else: stop_id = msg_id
            
        context.update({"step": "awaiting_range_selection", "start_id": start_id, "stop_id": stop_id})
        keyboard = create_range_keyboard(chat_id, start_id, stop_id)
        await bot.edit_message_text(
            chat_id=user_id, message_id=context["status_message_id"],
            text=f"Selected chat ID: `{chat_id}`.\n\nConfigure the scan range or continue.",
            reply_markup=keyboard
        )
        await message.delete() # Clean up the user's reply
        await message.reply_to_message.delete() # Clean up the bot's prompt

@Client.on_message(filters.private & ~filters.reply & ~filters.command("unequify"))
async def handle_chat_selection(bot: Client, message: Message):
    user_id = message.from_user.id
    context = user_context.get(user_id)
    if not context or context.get("step") != "awaiting_chat_selection": return

    try:
        selection = int(message.text)
        if 1 <= selection <= len(context["chats"]): chat_id = context["chats"][selection - 1]["id"]
        else: chat_id = selection
    except (ValueError, TypeError):
        await message.reply_text("Invalid input. Please reply with a number or a valid Chat ID.")
        return

    context.update({"step": "awaiting_range_selection", "chat_id": chat_id})
    keyboard = create_range_keyboard(chat_id)
    await message.reply_text(f"Selected chat ID: `{chat_id}`.\n\nConfigure the scan range.", reply_markup=keyboard)


# --- Step 3 & 4: DEDICATED CALLBACK HANDLERS ---

@Client.on_callback_query(filters.regex("^set_"))
async def handle_set_range(bot: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    try:
        _, step, chat_id_str, start_id_str, stop_id_str = cq.data.split("_")
        user_context[user_id].update({
            "step": f"awaiting_{step}_id",
            "status_message_id": cq.message.id
        })
        await cq.message.reply_text(f"Please **reply to this message** with the **{step} message ID**.", reply_markup=ForceReply(selective=True))
        await cq.answer()
    except Exception as e:
        await cq.answer(f"An error occurred: {e}", show_alert=True)
        if user_id in user_context: del user_context[user_id]

@Client.on_callback_query(filters.regex("^content_select_"))
async def handle_content_selection_menu(bot: Client, cq: CallbackQuery):
    try:
        _, chat_id_str, start_id_str, stop_id_str = cq.data.split("_")
        keyboard = create_content_keyboard(chat_id_str, start_id_str, stop_id_str)
        await cq.message.edit_text("**Select Content Types to Deduplicate**", reply_markup=keyboard)
    except Exception as e:
        await cq.answer(f"An error occurred: {e}", show_alert=True)
        if cq.from_user.id in user_context: del user_context[cq.from_user.id]

@Client.on_callback_query(filters.regex("^toggle_"))
async def handle_toggle_content(bot: Client, cq: CallbackQuery):
    try:
        _, state, index_str, chat_id_str, start_id_str, stop_id_str = cq.data.split("_")
        index = int(index_str)
        state_list = list(state)
        state_list[index] = '1' if state_list[index] == '0' else '0'
        new_state = "".join(state_list)
        keyboard = create_content_keyboard(chat_id_str, start_id_str, stop_id_str, new_state)
        await cq.message.edit_reply_markup(keyboard)
        await cq.answer()
    except Exception as e:
        await cq.answer(f"An error occurred: {e}", show_alert=True)

@Client.on_callback_query(filters.regex("^start_"))
async def handle_start_scan(bot: Client, cq: CallbackQuery):
    await start_deduplication_worker(bot, cq)

@Client.on_callback_query(filters.regex("^cancel_full"))
async def handle_cancel_full(bot: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    if user_id in user_context:
        del user_context[user_id]
    await cq.message.edit_text("Operation cancelled.")

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_context:
        del user_context[user_id]
        await message.reply_text("Current operation cancelled.")
    else:
        await message.reply_text("No active operation to cancel.")

# --- Final Step: The Main Worker Function ---

async def start_deduplication_worker(bot: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    status_message = cq.message
    await status_message.edit_text("`Finalizing settings...`", reply_markup=None)

    try:
        _, selection_state, chat_id_str, start_id_str, stop_id_str = cq.data.split("_", 4)
        target_channel_id = int(chat_id_str)
        start_message_id = int(start_id_str)
        stop_message_id = int(stop_id_str)
        
        selections = [OPTION_LABELS[i] for i, bit in enumerate(selection_state) if bit == '1']
        if not selections:
            await status_message.edit_text("❌ No types selected! Operation cancelled.")
            return

        await status_message.edit_text(f"`Initializing userbot session...\n\nTargeting: {', '.join(selections)}`")
        
        seen_identifiers, duplicates_to_delete = set(), []
        total_scanned, total_deleted = 0, 0

        async with Client(name=f"userbot_session_{user_id}", session_string=USERBOT_SESSION_STRING) as userbot:
            chat = await userbot.get_chat(target_channel_id)
            await status_message.edit_text(f"`Accessing: {chat.title}`\n\n`Checking permissions...`")
            member = await userbot.get_chat_member(chat.id, "me")
            
            is_authorized = member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
            can_delete = member.status == enums.ChatMemberStatus.OWNER or (member.privileges and member.privileges.can_delete_messages)

            if not (is_authorized and can_delete):
                await status_message.edit_text(f"❌ **Permission Denied in '{chat.title}'!**")
                return
            
            await status_message.edit_text(f"✅ **Permissions Confirmed!**\n\n`Starting scan...`")
            
            history_iterator = userbot.get_chat_history(chat.id, offset_id=start_message_id)

            async for msg in history_iterator:
                if stop_message_id != 0 and msg.id < stop_message_id: break
                total_scanned += 1
                identifier = None
                
                if selection_state[0] == '1' and msg.text: identifier = msg.text.strip()
                elif selection_state[1] == '1' and (msg.photo or msg.video) and msg.media: identifier = getattr(msg, msg.media.value).file_unique_id
                elif selection_state[2] == '1' and msg.audio: identifier = msg.audio.file_unique_id
                elif selection_state[3] == '1' and msg.document: identifier = msg.document.file_unique_id
                elif selection_state[4] == '1' and msg.sticker: identifier = msg.sticker.file_unique_id

                if identifier and identifier in seen_identifiers: duplicates_to_delete.append(msg.id)
                elif identifier: seen_identifiers.add(identifier)
                
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
        await status_message.edit_text(f"❌ **An unexpected error occurred:**\n\n`{e}`")
    finally:
        if user_id in user_context: del user_context[user_id]
