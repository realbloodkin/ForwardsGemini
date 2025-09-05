import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from database import db 
from config import API_ID, API_HASH # Ensure your bot's config.py provides these

# This dictionary holds the user's progress during the setup phase.
public_context = {}

@Client.on_message(filters.command(["forward_all", "past_forward"]) & filters.private)
async def past_forward_command(bot: Client, message: Message, chosen_client_info: dict = None):
    """
    Handles the entire past-forwarding process. This function is now two-stage:
    1. Client discovery and selection (if needed).
    2. Execution of your original forwarding logic with the selected client.
    """
    user_id = message.from_user.id
    
    # --- BLOCK 1: INJECTION - CLIENT DISCOVERY & SELECTION ---
    # This block only runs on the initial command, not on the callback-triggered continuation.
    if chosen_client_info is None:
        if user_id in public_context and public_context.get('task') and not public_context[user_id]['task'].done():
            return await message.reply_text("You already have a past-forwarding task running. Please wait for it to complete or restart the bot.")

        # Discover all available clients for the user
        available_clients = []
        bot_token_data = await db.get_bot(user_id)
        if bot_token_data and bot_token_data.get('is_bot'):
            available_clients.append({'type': 'bot_token', 'name': bot_token_data.get('name', 'Settings Bot')})

        userbots = bot.userbots.get(user_id, {})
        if 'db' in userbots and userbots['db'].is_connected:
            me = await userbots['db'].get_me()
            available_clients.append({'type': 'db_userbot', 'name': f"⚙️ Settings Userbot ({me.first_name})"})
        if 'cmd' in userbots and userbots['cmd'].is_connected:
            me = await userbots['cmd'].get_me()
            available_clients.append({'type': 'cmd_userbot', 'name': f"➕ Command Userbot ({me.first_name})"})

        if not available_clients:
            return await message.reply_text("❌ **No Client Found!**\n\nPlease add a bot or userbot via Settings or `/adduserbot`.")

        if len(available_clients) == 1:
            chosen_client_info = available_clients[0]
            await message.reply_text(f"Using the only available client: **{chosen_client_info['name']}**.")
        else:
            buttons = []
            for client in available_clients:
                buttons.append([InlineKeyboardButton(client['name'], callback_data=f"pastfwd_select_{client['type']}")])
            buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="pastfwd_cancel")])
            
            public_context[user_id] = {'original_message': message}
            await message.reply_text("Multiple clients found. Choose which one to use for this task:", reply_markup=InlineKeyboardMarkup(buttons))
            return # IMPORTANT: Pause the function until a button is pressed.
    
    # --- BLOCK 2: YOUR ORIGINAL FORWARDING LOGIC ---
    # This block runs only after a client has been chosen, using that specific client.
    forward_client = None
    try:
        # Step 2a: Instantiate the chosen client
        client_type = chosen_client_info['type']
        if client_type == 'bot_token':
            bot_data = await db.get_bot(user_id)
            forward_client = Client(name=f"pastfwd_bot_{user_id}", bot_token=bot_data['token'], api_id=API_ID, api_hash=API_HASH, in_memory=True)
        elif client_type == 'db_userbot':
            forward_client = bot.userbots[user_id]['db']
        elif client_type == 'cmd_userbot':
            forward_client = bot.userbots[user_id]['cmd']
        
        if not forward_client: raise ValueError("Could not initialize the selected client.")
        if not forward_client.is_connected: await forward_client.start()
        
        # Step 2b: Your original conversational setup and worker logic
        
        source_msg = await bot.ask(user_id, "Please forward a message from the **Source Channel**.\n\n`/cancel` to abort.", timeout=300)
        if source_msg.text == "/cancel": return await source_msg.reply_text("Cancelled.")
        source_id = source_msg.forward_from_chat.id

        target_msg = await bot.ask(user_id, "Now, forward a message from the **Target Channel**.", timeout=300)
        if target_msg.text == "/cancel": return await target_msg.reply_text("Cancelled.")
        target_id = target_msg.forward_from_chat.id

        start_id_msg = await bot.ask(user_id, "Send the **Start Message ID** (newest message). Reply with `0` to start from the very latest.", timeout=300)
        start_id = int(start_id_msg.text)
        
        stop_id_msg = await bot.ask(user_id, "Send the **Stop Message ID** (oldest message). Reply with `0` to process the entire history.", timeout=300)
        stop_id = int(stop_id_msg.text)

        status_msg = await bot.send_message(user_id, "✅ Setup complete. The task is starting now...")
        
        total_forwarded = 0
        source_chat = await forward_client.get_chat(source_id)
        target_chat = await forward_client.get_chat(target_id)
        
        await status_msg.edit_text(f"Starting to forward from **{source_chat.title}** to **{target_chat.title}**.")
        
        async for msg in forward_client.get_chat_history(source_chat.id, offset_id=start_id):
            if stop_id != 0 and msg.id < stop_id:
                break
            
            try:
                # YOUR ORIGINAL FILTERING/CAPTION LOGIC would be applied to the `msg` object here.
                await msg.copy(target_chat.id)
                total_forwarded += 1
                if total_forwarded % 20 == 0: # Status update every 20 messages
                    await status_msg.edit_text(f"⚙️ In progress... Forwarded **{total_forwarded}** messages.")
                    await asyncio.sleep(5) # Rate limiting
            except Exception as e:
                await bot.send_message(user_id, f"⚠️ Could not forward message `{msg.id}`.\n**Reason:** `{e}`")

        await status_msg.edit_text(f"✅ **Task Complete!**\n\nSuccessfully forwarded **{total_forwarded}** messages.")
        
    except (asyncio.TimeoutError, ValueError):
        await bot.send_message(user_id, "Setup timed out or invalid input. Operation cancelled.")
    except Exception as e:
        await bot.send_message(user_id, f"❌ **An error occurred:**\n`{e}`")
    finally:
        # Clean up the on-the-fly bot token client
        if forward_client and forward_client.is_connected and chosen_client_info and chosen_client_info['type'] == 'bot_token':
            await forward_client.stop()
        if user_id in public_context:
            del public_context[user_id]


@Client.on_callback_query(filters.regex("^pastfwd_select_"))
async def handle_pastfwd_client_selection(bot: Client, cq: CallbackQuery):
    """
    This new handler catches the button press, selects the client,
    and then re-calls the main command function to continue the process.
    """
    user_id = cq.from_user.id
    context = public_context.get(user_id)

    if not context or not context.get('original_message'):
        return await cq.message.edit_text("This selection has expired. Please start the command again.")

    client_type = cq.data.split("_")[-1]
    original_message = context['original_message']
    
    client_info = {}
    if client_type == 'bot_token':
        bot_data = await db.get_bot(user_id)
        client_info = {'type': 'bot_token', 'name': bot_data.get('name')}
    elif client_type == 'db_userbot':
        me = await bot.userbots[user_id]['db'].get_me()
        client_info = {'type': 'db_userbot', 'name': f"Settings Userbot ({me.first_name})"}
    elif client_type == 'cmd_userbot':
        me = await bot.userbots[user_id]['cmd'].get_me()
        client_info = {'type': 'cmd_userbot', 'name': f"Command Userbot ({me.first_name})"}
    
    if not client_info:
        return await cq.message.edit_text("❌ Error: The selected client is no longer available.")

    await cq.message.delete()
    
    # Re-call the main command function, passing the chosen client info to it.
    await past_forward_command(bot, original_message, chosen_client_info=client_info)

@Client.on_callback_query(filters.regex("^pastfwd_cancel"))
async def handle_pastfwd_cancel(bot: Client, cq: CallbackQuery):
    if cq.from_user.id in public_context:
        del public_context[cq.from_user.id]
    await cq.message.edit_text("Operation cancelled.")
