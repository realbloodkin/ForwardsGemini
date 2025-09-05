from pyrogram import Client, filters
from pyrogram.types import Message
from database import db 

@Client.on_message(filters.command("adduserbot") & filters.private)
async def add_command_userbot(bot: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in bot.userbots:
        bot.userbots[user_id] = {}
        
    if 'cmd' in bot.userbots[user_id]:
        return await message.reply_text("You already have a userbot added via command. Use `/removeuserbot` first.")
        
    try:
        session_msg = await bot.ask(user_id, "Please send your **Pyrogram V2 session string**.", timeout=300)
        session_string = session_msg.text.strip()
        
        status_msg = await message.reply_text("`Validating session and logging in...`")
        
        userbot_client = Client(name=f"userbot_cmd_{user_id}", session_string=session_string, in_memory=True)
        await userbot_client.start()
        userbot_info = await userbot_client.get_me()
        
        await db.update_configs(user_id, 'command_userbot_session', session_string)
        
        bot.userbots[user_id]['cmd'] = userbot_client
        
        await status_msg.edit_text(f"✅ **Command Userbot added successfully!**\n**Name:** {userbot_info.first_name}")

    except Exception as e:
        await message.reply_text(f"❌ **Failed to add command userbot:**\n`{e}`")

@Client.on_message(filters.command("removeuserbot") & filters.private)
async def remove_command_userbot(bot: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id in bot.userbots and 'cmd' in bot.userbots[user_id]:
        userbot_client = bot.userbots[user_id]['cmd']
        
        if userbot_client.is_connected:
            await userbot_client.stop()
        
        del bot.userbots[user_id]['cmd']
        
        await db.update_configs(user_id, 'command_userbot_session', None)
        
        await message.reply_text("✅ Command userbot has been removed successfully.")
    else:
        await message.reply_text("You don't have a userbot registered via command.")
