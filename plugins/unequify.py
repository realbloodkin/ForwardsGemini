import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply

user_context = {} 

# --- Keyboards & Constants (Complete) ---
OPTION_LABELS = ["Text", "Photos/Videos", "Audio", "Documents", "Stickers"]
def create_range_keyboard(chat_id, start_id=0, stop_id=0):
    start_text = "Latest" if start_id == 0 else f"{start_id}"
    stop_text = "Oldest" if stop_id == 0 else f"{stop_id}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Scan Range: {start_text} ➡️ {stop_text}", callback_data="unequify_noop")],
        [
            InlineKeyboardButton("Set Start ID", callback_data=f"unequify_set_start_{chat_id}_{start_id}_{stop_id}"),
            InlineKeyboardButton("Set Stop ID", callback_data=f"unequify_set_stop_{chat_id}_{start_id}_{stop_id}")
        ],
        [InlineKeyboardButton("✅ Continue", callback_data=f"unequify_content_select_{chat_id}_{start_id}_{stop_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="unequify_cancel_full")]
    ])
def create_content_keyboard(chat_id, start_id, stop_id, selection_state="01010"):
    buttons = []
    state_list = list(selection_state)
    for i, label in enumerate(OPTION_LABELS):
        text = f"✅ {label}" if state_list[i] == '1' else label
        buttons.append([InlineKeyboardButton(text, callback_data=f"unequify_toggle_{selection_state}_{i}_{chat_id}_{start_id}_{stop_id}")])
    buttons.append([
        InlineKeyboardButton("🚀 Start Scan", callback_data=f"unequify_start_{selection_state}_{chat_id}_{start_id}_{stop_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data="unequify_cancel_full")
    ])
    return InlineKeyboardMarkup(buttons)

# --- Main Command & Userbot Selection ---
@Client.on_message(filters.command("unequify") & filters.private)
async def unequify_command_start(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_context:
        return await message.reply_text("A previous unequify operation is in progress. Use /cancel first.")

    available_bots = bot.userbots.get(user_id, {})
    db_bot = available_bots.get('db')
    cmd_bot = available_bots.get('cmd')

    if not db_bot and not cmd_bot:
        return await message.reply_text("❌ **No Userbot Found!**\n\nPlease add a userbot via Settings or `/adduserbot`.")

    if db_bot and not cmd_bot: return await proceed_to_chat_listing(message, db_bot, 'db')
    if not db_bot and cmd_bot: return await proceed_to_chat_listing(message, cmd_bot, 'cmd')
    
    buttons = []
    db_info = await db_bot.get_me()
    cmd_info = await cmd_bot.get_me()
    buttons.append([InlineKeyboardButton(f"⚙️ Settings Userbot ({db_info.first_name})", callback_data="unequify_select_db")])
    buttons.append([InlineKeyboardButton(f"➕ Command Userbot ({cmd_info.first_name})", callback_data="unequify_select_cmd")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="unequify_cancel_full")])
    
    user_context[user_id] = {"step": "awaiting_userbot_selection"}
    await message.reply_text("Multiple userbots found. Choose one for this operation:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^unequify_select_"))
async def select_userbot_for_unequify(bot: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    bot_type = cq.data.split("_")[-1]

    userbot_client = bot.userbots.get(user_id, {}).get(bot_type)
    if not userbot_client:
        return await cq.message.edit_text("❌ Error: Selected userbot is no longer available.")

    await cq.message.delete()
    await proceed_to_chat_listing(cq.message, userbot_client, bot_type)

async def proceed_to_chat_listing(message: Message, userbot_client: Client, bot_type: str):
    user_id = message.chat.id
    status_message = await message.reply_text(f"`Authenticating with '{bot_type.upper()}' userbot...`")
    try:
        if not userbot_client.is_connected: await userbot_client.start()
        await status_message.edit_text("`Fetching chat list...`")
        chat_list = []
        async for dialog in userbot_client.get_dialogs():
            if dialog.chat.type in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP]:
                chat_list.append({"id": dialog.chat.id, "title": dialog.chat.title})
        if not chat_list:
            return await status_message.edit_text("❌ **No channels or supergroups found**.")
        user_context[user_id] = {"step": "awaiting_chat_selection", "chats": chat_list, "userbot_type": bot_type}
        response_text = "**Select a Channel/Supergroup**\n\nReply with the number or Chat ID:\n\n"
        for i, chat in enumerate(chat_list, 1):
            response_text += f"**{i}.** `{chat['title']}` (ID: `{chat['id']}`)\n"
        await status_message.edit_text(response_text, disable_web_page_preview=True)
    except Exception as e:
        await status_message.edit_text(f"❌ **Error:**\n`{e}`")
        if user_id in user_context: del user_context[user_id]

# --- Conversational Handlers (Full, Robust Version) ---
@Client.on_message(filters.private & ~filters.command(["unequify", "cancel", "adduserbot", "removeuserbot", "settings", "forward_all", "past_forward"]))
async def handle_unequify_text_input(bot: Client, message: Message):
    user_id = message.from_user.id
    context = user_context.get(user_id)
    if not context: return

    if context.get("step") == "awaiting_chat_selection":
        try:
            selection = int(message.text)
            chat_id = context["chats"][selection - 1]["id"] if 1 <= selection <= len(context["chats"]) else selection
        except (ValueError, TypeError, IndexError):
            return await message.reply_text("Invalid input. Reply with a number from the list or a valid Chat ID.")
        context.update({"step": "awaiting_range_selection", "chat_id": chat_id})
        await message.reply_text(f"Selected chat ID: `{chat_id}`.\nConfigure scan range.", reply_markup=create_range_keyboard(chat_id))

    elif context.get("step") in ["awaiting_start_id", "awaiting_stop_id"] and message.reply_to_message:
        try:
            msg_id = int(message.text)
            if msg_id < 0: raise ValueError # Message IDs can't be negative
        except (ValueError, TypeError):
            return await message.reply_text("Invalid Message ID. Please enter a positive number.")
        
        chat_id = context["chat_id"]
        start_id = context.get("start_id", 0)
        stop_id = context.get("stop_id", 0)
        if context["step"] == "awaiting_start_id": start_id = msg_id
        else: stop_id = msg_id
            
        context.update({"step": "awaiting_range_selection", "start_id": start_id, "stop_id": stop_id})
        await bot.edit_message_text(user_id, context["status_message_id"], f"Selected chat ID: `{chat_id}`.", reply_markup=create_range_keyboard(chat_id, start_id, stop_id))
        await message.delete()
        await message.reply_to_message.delete()

@Client.on_callback_query(filters.regex("^unequify_"))
async def handle_unequify_callbacks(bot: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    data = cq.data.replace("unequify_", "") 
    if not user_context.get(user_id):
        return await cq.message.edit_text("This operation has expired. Please start again.")

    if data.startswith("set_"):
        _, step, chat_id, start_id, stop_id = data.split("_")
        user_context[user_id]["step"] = f"awaiting_{step}_id"
        user_context[user_id]["status_message_id"] = cq.message.id
        await cq.message.reply_text(f"Please **reply to this message** with the **{step} message ID**.", reply_markup=ForceReply(selective=True))
    elif data.startswith("content_select_"):
        _, chat_id, start_id, stop_id = data.split("_")
        await cq.message.edit_text("**Select Content Types to Deduplicate**", reply_markup=create_content_keyboard(chat_id, start_id, stop_id))
    elif data.startswith("toggle_"):
        _, state, index, chat_id, start_id, stop_id = data.split("_")
        state_list = list(state); state_list[int(index)] = '1' if state_list[int(index)] == '0' else '0'
        await cq.message.edit_reply_markup(create_content_keyboard(chat_id, start_id, stop_id, "".join(state_list)))
    elif data.startswith("start_"):
        await start_deduplication_worker(bot, cq)
    elif data == "cancel_full":
        del user_context[user_id]
        await cq.message.edit_text("Operation cancelled.")
    await cq.answer()

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(bot: Client, message: Message):
    if message.from_user.id in user_context:
        del user_context[message.from_user.id]
        await message.reply_text("Current unequify operation cancelled.")
    else:
        await message.reply_text("No active unequify operation to cancel.")

# --- The Main Worker Function (Final Version) ---
async def start_deduplication_worker(bot: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    context = user_context.get(user_id)
    if not context: return
    status_message = cq.message
    await status_message.edit_text("`Finalizing settings...`", reply_markup=None)
    
    userbot = bot.userbots.get(user_id, {}).get(context.get("userbot_type"))
    if not userbot or not userbot.is_connected:
        return await status_message.edit_text("❌ Userbot disconnected!")
    
    try:
        data = cq.data.replace("unequify_", "")
        _, state, chat_id, start_id, stop_id = data.split("_", 4)
        target_id, start_id, stop_id = int(chat_id), int(start_id), int(stop_id)
        
        selections = [OPTION_LABELS[i] for i, bit in enumerate(state) if bit == '1']
        if not selections: return await status_message.edit_text("❌ No types selected!")

        await status_message.edit_text(f"`Accessing channel...`")
        chat = await userbot.get_chat(target_id)
        member = await userbot.get_chat_member(chat.id, "me")
        
        is_admin = member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
        can_delete = member.status == enums.ChatMemberStatus.OWNER or (member.privileges and member.privileges.can_delete_messages)
        if not (is_admin and can_delete):
            return await status_message.edit_text(f"❌ **Permission Denied in '{chat.title}'!**")
        
        await status_message.edit_text(f"✅ **Permissions Confirmed!**\n`Scanning...`")
        seen, to_delete, scanned, deleted = set(), [], 0, 0
        
        async for msg in userbot.get_chat_history(chat.id, offset_id=start_id):
            if stop_id != 0 and msg.id < stop_id: break
            scanned += 1
            identifier = None
            if state[0] == '1' and msg.text: identifier = msg.text.strip()
            elif state[1] == '1' and (msg.photo or msg.video) and msg.media: identifier = getattr(msg, msg.media.value).file_unique_id
            elif state[2] == '1' and msg.audio and msg.audio.file_unique_id: identifier = msg.audio.file_unique_id
            elif state[3] == '1' and msg.document and msg.document.file_unique_id: identifier = msg.document.file_unique_id
            elif state[4] == '1' and msg.sticker and msg.sticker.file_unique_id: identifier = msg.sticker.file_unique_id

            if identifier and identifier in seen: to_delete.append(msg.id)
            elif identifier: seen.add(identifier)
            
            if len(to_delete) >= 100:
                await userbot.delete_messages(chat.id, to_delete)
                deleted += len(to_delete); to_delete.clear()
                await status_message.edit_text(f"⚙️ Scanned: `{scanned}` | Deleted: `{deleted}`")
                await asyncio.sleep(3)
        
        if to_delete:
            await userbot.delete_messages(chat.id, to_delete)
            deleted += len(to_delete)

        await status_message.edit_text(f"✅ **Complete!**\n\nScanned: `{scanned}`\nDeleted: `{deleted}`")
    except Exception as e:
        await status_message.edit_text(f"❌ **Error:**\n`{e}`")
    finally:
        if user_id in user_context: del user_context[user_id]
