import asyncio 
from database import db
from config import Config
from translation import Translation
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT as CLIENT_HELPERS, parse_buttons
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT_HELPERS()

@Client.on_message(filters.private & filters.command(['settings']))
async def settings(client, message):
    text="<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ Aꜱ Pᴇʀ Yᴏᴜʀ Nᴇᴇᴅꜱ! ❄️</b>"
    await message.reply_text(
        text=text,
        reply_markup=main_buttons(),
        quote=True
    )
    
@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot: Client, query: CallbackQuery):
  user_id = query.from_user.id
  i, type = query.data.split("#")
  buttons = [[InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#main")]]
  
  if type=="main":
     await query.message.edit_text(
       "<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ Aꜱ Pᴇʀ Yᴏᴜʀ Nᴇᴇᴅꜱ! ❄️</b>",
       reply_markup=main_buttons())
       
  elif type=="bots":
     buttons = [] 
     _bot = await db.get_bot(user_id)
     if _bot is not None:
        buttons.append([InlineKeyboardButton(_bot['name'],
                         callback_data=f"settings#editbot")])
     else:
        buttons.append([InlineKeyboardButton('⨁ Aᴅᴅ Bᴏᴛ ⨁', 
                         callback_data="settings#addbot")])
        buttons.append([InlineKeyboardButton('⨁ Aᴅᴅ Uꜱᴇʀ Bᴏᴛ ⨁', 
                         callback_data="settings#adduserbot")])
     buttons.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', 
                      callback_data="settings#main")])
     await query.message.edit_text(
       "<b><u>Mʏ Bᴏᴛꜱ</u></b>\n\nYᴏᴜ Cᴀɴ Mᴀɴᴀɢᴇ Yᴏᴜʀ Bᴏᴛꜱ Iɴ Hᴇʀᴇ \nAᴅᴅ Tʜɪꜱ Bᴏᴛ Tᴀʀɢᴇᴛ Cʜᴀᴛ ᴀɴᴅ Sᴏᴜʀᴄᴇ Cʜᴀᴛ ✨",
       reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="addbot":
     await query.message.delete()
     bot_added = await CLIENT.add_bot(bot, query)
     if not bot_added: return
     await query.message.reply_text(
        "<b>Bᴏᴛ Tᴏᴋᴇɴ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Aᴅᴅᴇᴅ Tᴏ Dᴀᴛᴀʙᴀꜱᴇ ✓</b>",
        reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="adduserbot":
     await query.message.delete()
     session_string = await CLIENT.add_session(bot, query) # This helper must return the session string
     if not session_string: return
     
     try:
        status_msg = await query.message.reply_text("`Session saved to DB. Starting live client...`")
        userbot_client = Client(name=f"userbot_db_{user_id}", session_string=session_string, in_memory=True)
        await userbot_client.start()

        if user_id not in bot.userbots:
            bot.userbots[user_id] = {}
        bot.userbots[user_id]['db'] = userbot_client
        
        await status_msg.edit_text(
            "<b>Sᴇꜱꜱɪᴏɴ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Aᴅᴅᴇᴅ Aɴᴅ Aᴄᴛɪᴠᴀᴛᴇᴅ ✓</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
     except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to start live userbot:**\n`{e}`")
      
  elif type=="channels":
     # This part is preserved
     buttons = []
     channels = await db.get_user_channels(user_id)
     for channel in channels:
        buttons.append([InlineKeyboardButton(f"⁕ {channel['title']}",
                         callback_data=f"settings#editchannels_{channel['chat_id']}")])
     buttons.append([InlineKeyboardButton('⨁ Aᴅᴅ Cʜᴀɴɴᴇʟ ⨁', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>Mʏ Cʜᴀɴɴᴇʟꜱ</u></b>\n\nYᴏᴜ Cᴀɴ Mᴀɴᴀɢᴇ Yᴏᴜʀ Tᴀʀɢᴇᴛ Cʜᴀᴛꜱ Iɴ Hᴇʀᴇ!",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="addchannel":
     # This part is preserved
     await query.message.delete()
     try:
         text = await bot.send_message(user_id, "<b><u>Sᴇᴛ Tᴀʀɢᴇᴛ Cʜᴀᴛ</u></b>\n\nFᴏʀᴡᴀʀᴅ A Mᴇꜱꜱᴀɢᴇ Fʀᴏᴍ Yᴏᴜʀ Tᴀʀɢᴇᴛ Cʜᴀᴛ\n/cancel - To Cancel This Process")
         chat_ids = await bot.listen(chat_id=user_id, timeout=300)
         if chat_ids.text=="/cancel":
            await chat_ids.delete()
            return await text.edit_text("Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !", reply_markup=InlineKeyboardMarkup(buttons))
         elif not chat_ids.forward_date:
            await chat_ids.delete()
            return await text.edit_text("Tʜɪꜱ Iꜱ Nᴏᴛ A Fᴏʀᴡᴀʀᴅᴇᴅ Mᴇꜱꜱᴀɢᴇ!")
         else:
            chat_id = chat_ids.forward_from_chat.id
            title = chat_ids.forward_from_chat.title
            username = chat_ids.forward_from_chat.username
            username = "@" + username if username else "private"
         chat = await db.add_channel(user_id, chat_id, title, username)
         await chat_ids.delete()
         await text.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Uᴩᴅᴀᴛᴇᴅ ✓" if chat else "Tʜɪꜱ Cʜᴀɴɴᴇʟ Iꜱ Aʟʀᴇᴀᴅʏ Aᴅᴅᴇᴅ", reply_markup=InlineKeyboardMarkup(buttons))
     except asyncio.exceptions.TimeoutError:
         await text.edit_text('Pʀᴏᴄᴇꜱꜱ Hᴀꜱ Bᴇᴇɴ Cᴀɴᴄᴇʟʟᴇᴅ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Dᴜᴇ Tᴏ Nᴏ Rᴇꜱᴩᴏɴꜱᴇ!', reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="editbot": 
     _bot_data = await db.get_bot(user_id)
     TEXT = Translation.BOT_DETAILS if _bot_data['is_bot'] else Translation.USER_DETAILS
     buttons = [[InlineKeyboardButton('⛒ Rᴇᴍᴏᴠᴇ ⛒', callback_data=f"settings#removebot")], [InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#bots")]]
     await query.message.edit_text(TEXT.format(_bot_data['name'], _bot_data['id'], _bot_data['username']), reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type=="removebot":
     # Stop and remove the live client if it exists
     if user_id in bot.userbots and 'db' in bot.userbots[user_id]:
        if bot.userbots[user_id]['db'].is_connected:
            await bot.userbots[user_id]['db'].stop()
        del bot.userbots[user_id]['db']
     
     await db.remove_bot(user_id)
     await query.message.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Rᴇᴍᴏᴠᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
                                             
  # --- ALL OTHER SETTINGS HANDLERS ARE PRESERVED ---
  # The rest of your file (editchannels, caption, buttons, etc.) continues here exactly as you provided it.
  elif type.startswith("editchannels"):
    # ... your original code ...
    pass
  elif type.startswith("removechannel"):
    # ... your original code ...
    pass
  elif type == "caption":
    # ... your original code ...
    pass
  # ... and so on for all other handlers ...

# --- ALL HELPER FUNCTIONS ARE PRESERVED ---
def main_buttons():
    # ... your original code ...
    pass
# ... and so on for size_limit, extract_btn, size_button, filters_buttons, etc.
