import asyncio 
from database import db
from config import Config
from translation import Translation
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT as CLIENT_HELPERS, parse_buttons
# --- THIS LINE HAS BEEN CORRECTED ---
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

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
     session_string = await CLIENT.add_session(bot, query)
     if not session_string: return
     
     try:
        status_msg = await query.message.reply_text("`Session saved. Starting live client...`")
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
     if user_id in bot.userbots and 'db' in bot.userbots[user_id]:
        if bot.userbots[user_id]['db'].is_connected:
            await bot.userbots[user_id]['db'].stop()
        del bot.userbots[user_id]['db']
     
     await db.remove_bot(user_id)
     await query.message.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Rᴇᴍᴏᴠᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type.startswith("editchannels"): 
     chat_id = type.split('_')[1]
     chat = await db.get_channel_details(user_id, chat_id)
     buttons = [[InlineKeyboardButton('⛒ Rᴇᴍᴏᴠᴇ ⛒', callback_data=f"settings#removechannel_{chat_id}")], [InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>📄 Cʜᴀɴɴᴇʟ Dᴇᴛᴀɪʟꜱ</b></u>\n\n<b>Tɪᴛʟᴇ :</b> <code>{chat['title']}</code>\n<b>Cʜᴀɴɴᴇʟ ID :</b> <code>{chat['chat_id']}</code>\n<b>Uꜱᴇʀɴᴀᴍᴇ :</b> {chat['username']}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type.startswith("removechannel"):
     chat_id = type.split('_')[1]
     await db.remove_channel(user_id, chat_id)
     await query.message.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Uᴩᴅᴀᴛᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
                               
  elif type=="caption":
     buttons = []
     data = await get_configs(user_id)
     caption = data['caption']
     if caption is None:
        buttons.append([InlineKeyboardButton('⨁ Aᴅᴅ Cᴀᴩᴛɪᴏɴ ⨁', callback_data="settings#addcaption")])
     else:
        buttons.append([InlineKeyboardButton('↳ Sᴇᴇ Cᴀᴩᴛɪᴏɴ', callback_data="settings#seecaption")])
        buttons[-1].append(InlineKeyboardButton('↳ Dᴇʟᴇᴛᴇ Cᴀᴩᴛɪᴏɴ', callback_data="settings#deletecaption"))
     buttons.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>Custom Caption</b></u>\n\nYou Can Set A Custom Caption To Videos And Documents. Normaly Use Its Default Caption\n\n<b><u>Available Fillings :</b></u>\n\n<code>{filename}</code> : Filename\n<code>{size}</code> : File Size\n<code>{caption}</code> : Default Caption",
        reply_markup=InlineKeyboardMarkup(buttons))
                               
  elif type=="seecaption":   
     data = await get_configs(user_id)
     buttons = [[InlineKeyboardButton('↳ Eᴅɪᴛ Cᴀᴩᴛɪᴏɴ', callback_data="settings#addcaption")], [InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#caption")]]
     await query.message.edit_text(f"<b><u>Your Custom Caption</b></u>\n\n<code>{data['caption']}</code>", reply_markup=InlineKeyboardMarkup(buttons))
    
  elif type=="deletecaption":
     await update_configs(user_id, 'caption', None)
     await query.message.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Uᴩᴅᴀᴛᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
                              
  elif type=="addcaption":
     await query.message.delete()
     try:
         text = await bot.send_message(query.message.chat.id, "Send your custom caption\n/cancel - <code>cancel this process</code>")
         caption = await bot.listen(chat_id=user_id, timeout=300)
         if caption.text=="/cancel":
            await caption.delete()
            return await text.edit_text("Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !", reply_markup=InlineKeyboardMarkup(buttons))
         try:
            caption.text.format(filename='', size='', caption='')
         except KeyError as e:
            await caption.delete()
            return await text.edit_text(f"Wrong Filling {e} Used In Your Caption. Change It", reply_markup=InlineKeyboardMarkup(buttons))
         await update_configs(user_id, 'caption', caption.text)
         await caption.delete()
         await text.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Uᴩᴅᴀᴛᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
     except asyncio.exceptions.TimeoutError:
         await text.edit_text('Process Has Been Automatically Cancelled', reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="button":
     buttons = []
     button = (await get_configs(user_id))['button']
     if button is None:
        buttons.append([InlineKeyboardButton('⨁ Aᴅᴅ Bᴜᴛᴛᴏɴ ⨁', callback_data="settings#addbutton")])
     else:
        buttons.append([InlineKeyboardButton('↳ Sᴇᴇ Bᴜᴛᴛᴏɴ', callback_data="settings#seebutton")])
        buttons[-1].append(InlineKeyboardButton('↳ Rᴇᴍᴏᴠᴇ Bᴜᴛᴛᴏɴ ', callback_data="settings#deletebutton"))
     buttons.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>Cᴜꜱᴛᴏᴍ Bᴜᴛᴛᴏɴ</b></u>\n\nYᴏᴜ Cᴀɴ Sᴇᴛ Aɴ Iɴʟɪɴᴇ Bᴜᴛᴛᴏɴ To Mᴇꜱꜱᴀɢᴇꜱ Wʜɪᴄʜ Wɪʟʟ Bᴇ Fᴏʀᴡᴀʀᴅᴇᴅ.\n\n<b><u>Fᴏʀᴍᴀᴛ :</b></u>\n`[Mᴏᴅ Mᴏᴠɪᴇᴢ x][buttonurl:https://t.me/Mod_Moviez_X]`\n",
        reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="addbutton":
     await query.message.delete()
     try:
         txt = await bot.send_message(user_id, text="**Send your custom button.\n\nFORMAT:**\n`[forward bot][buttonurl:https://t.me/KR_Forward_Bot]`\n")
         ask = await bot.listen(chat_id=user_id, timeout=300)
         button = parse_buttons(ask.text.html)
         if not button:
            await ask.delete()
            return await txt.edit_text("Iɴᴠᴀʟɪᴅ Bᴜᴛᴛᴏɴ ⛒")
         await update_configs(user_id, 'button', ask.text.html)
         await ask.delete()
         await txt.edit_text("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Bᴜᴛᴛᴏɴ Aᴅᴅᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
     except asyncio.exceptions.TimeoutError:
         await txt.edit_text('Process Has Been Automatically Cancelled', reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="seebutton":
      button = (await get_configs(user_id))['button']
      button = parse_buttons(button, markup=False)
      button.append([InlineKeyboardButton("⇇ Bᴀᴄᴋ", "settings#button")])
      await query.message.edit_text("**Your Custom Button**", reply_markup=InlineKeyboardMarkup(button))
      
  elif type=="deletebutton":
     await update_configs(user_id, 'button', None)
     await query.message.edit_text("Successfully Button Deleted", reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="database":
     buttons = []
     db_uri = (await get_configs(user_id))['db_uri']
     if db_uri is None:
        buttons.append([InlineKeyboardButton('⨁ Add URL ⨁', callback_data="settings#addurl")])
     else:
        buttons.append([InlineKeyboardButton('↳ See URL', callback_data="settings#seeurl")])
        buttons[-1].append(InlineKeyboardButton('↳ Remove URL', callback_data="settings#deleteurl"))
     buttons.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>Database</u></b>\n\nDatabase Is Required For Store Your Duplicate Messages Permenant. Other Wise Stored Duplicate Media May Be Disappeared When After Bot Restart.",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addurl":
     await query.message.delete()
     uri = await bot.ask(user_id, "<b>please send your mongodb url.</b>\n\n<i>get your Mongodb url from [here](https://mongodb.com)</i>", disable_web_page_preview=True)
     if uri.text=="/cancel":
        return await uri.reply_text("Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !", reply_markup=InlineKeyboardMarkup(buttons))
     if not uri.text.startswith("mongodb+srv://") and not uri.text.endswith("majority"):
        return await uri.reply("Iɴᴠᴀʟɪᴅ MᴏɴɢᴏDB Uʀʟ ⛒, Aᴠᴏᴏᴅ '/' Iɴ Eɴᴅ Iꜰ Tʜᴇʀᴇ Iᴛ Iꜱ Aᴠᴀɪʟᴀʙʟᴇ", reply_markup=InlineKeyboardMarkup(buttons))
     await update_configs(user_id, 'db_uri', uri.text)
     await uri.reply("Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Dᴀᴛᴀʙᴀꜱᴇ Uʀʟ Aᴅᴅᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="seeurl":
     db_uri = (await get_configs(user_id))['db_uri']
     await query.answer(f"Dᴀᴛᴀʙᴀꜱᴇ Uʀʟ : {db_uri}", show_alert=True)
  
  elif type=="deleteurl":
     await update_configs(user_id, 'db_uri', None)
     await query.message.edit_text("Successfully Your Database URL Deleted", reply_markup=InlineKeyboardMarkup(buttons))
      
  elif type=="filters":
     await query.message.edit_text(
        "<b><u>Custom Filters</u></b>\n\nConfigure The Type Of Messages Which You Want Forward",
        reply_markup=await filters_buttons(user_id))
  
  elif type=="nextfilters":
     await query.edit_message_reply_markup(reply_markup=await next_filters_buttons(user_id))
   
  elif type.startswith("updatefilter"):
     i, key, value = type.split('-')
     if value=="True":
        await update_configs(user_id, key, False)
     else:
        await update_configs(user_id, key, True)
     if key in ['poll', 'protect']:
        return await query.edit_message_reply_markup(reply_markup=await next_filters_buttons(user_id)) 
     await query.edit_message_reply_markup(reply_markup=await filters_buttons(user_id))
   
  elif type.startswith("file_size"):
    settings = await get_configs(user_id)
    size = settings.get('file_size', 0)
    i, limit = size_limit(settings['size_limit'])
    await query.message.edit_text(
       f'<b><u>Sɪᴢᴇ Lɪᴍɪᴛ</u></b>\n\nYᴏᴜ Cᴀɴ Sᴇᴛ Fɪʟᴇ Sɪᴢᴇ Lɪᴍɪᴛ To Fᴏᴡᴀʀᴅ\n\nSᴛᴀᴛᴜꜱ : Fɪʟᴇꜱ Wɪᴛʜ {limit} `{size} ᴍʙ` Wɪʟʟ Bᴇ Fᴏʀᴡᴀʀᴅ',
       reply_markup=size_button(size))
  
  elif type.startswith("update_size"):
    size = int(query.data.split('-')[1])
    if 0 < size > 2000:
      return await query.answer("Size Limit Exceeded", show_alert=True)
    await update_configs(user_id, 'file_size', size)
    i, limit = size_limit((await get_configs(user_id))['size_limit'])
    await query.message.edit_text(
       f'<b><u>Sɪᴢᴇ Lɪᴍɪᴛ</u></b>\n\nYᴏᴜ Fᴏᴡᴀʀᴅ Tᴏ Fᴏᴡᴀʀᴅ\n\nSᴛᴀᴛᴜꜱ : Fɪʟᴇꜱ Wɪᴛʜ {limit} `{size} ᴍʙ` Wɪʟʟ Bᴇ Fᴏʀᴡᴀʀᴅ',
       reply_markup=size_button(size))
  
  elif type.startswith('update_limit'):
    i, limit, size = type.split('-')
    limit, sts = size_limit(limit)
    await update_configs(user_id, 'size_limit', limit) 
    await query.message.edit_text(
       f'<b><u>Size Limit</u></b>\n\nYou Can Set File Size Limit To Forward\n\nStatus : Files With {sts} `{size} MB` Will Forward',
       reply_markup=size_button(int(size)))
      
  elif type == "add_extension":
    await query.message.delete() 
    ext = await bot.ask(user_id, text="Please Send Your Extensions (Seperete By Space)")
    if ext.text == '/cancel':
       return await ext.reply_text("Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !", reply_markup=InlineKeyboardMarkup(buttons))
    extensions = ext.text.split(" ")
    extension = (await get_configs(user_id))['extension']
    if extension:
        for extn in extensions:
            extension.append(extn)
    else:
        extension = extensions
    await update_configs(user_id, 'extension', extension)
    await ext.reply_text(f"Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Uᴩᴅᴀᴛᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
      
  elif type == "get_extension":
    extensions = (await get_configs(user_id))['extension']
    btn = extract_btn(extensions)
    btn.append([InlineKeyboardButton('⨁ Add ⨁', 'settings#add_extension')])
    btn.append([InlineKeyboardButton('Remove All', 'settings#rmve_all_extension')])
    btn.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', 'settings#main')])
    await query.message.edit_text(
        text='<b><u>Extensions</u></b>\n\nFiles With These Extiontions Will Not Forward',
        reply_markup=InlineKeyboardMarkup(btn))
  
  elif type == "rmve_all_extension":
    await update_configs(user_id, 'extension', None)
    await query.message.edit_text(text="Successfully Deleted", reply_markup=InlineKeyboardMarkup(buttons))
  elif type == "add_keyword":
    await query.message.delete()
    ask = await bot.ask(user_id, text="Please Send The Keywords (Seperete By Space)")
    if ask.text == '/cancel':
       return await ask.reply_text("Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !", reply_markup=InlineKeyboardMarkup(buttons))
    keywords = ask.text.split(" ")
    keyword = (await get_configs(user_id))['keywords']
    if keyword:
        for word in keywords:
            keyword.append(word)
    else:
        keyword = keywords
    await update_configs(user_id, 'keywords', keyword)
    await ask.reply_text(f"Sᴜᴄᴄᴇꜱꜱꜰᴜʟʏ Uᴩᴅᴀᴛᴇᴅ ✓", reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type == "get_keyword":
    keywords = (await get_configs(user_id))['keywords']
    btn = extract_btn(keywords)
    btn.append([InlineKeyboardButton('⨁ Aᴅᴅ ⨁', 'settings#add_keyword')])
    btn.append([InlineKeyboardButton('Rᴇᴍᴏᴠᴇ Aʟʟ', 'settings#rmve_all_keyword')])
    btn.append([InlineKeyboardButton('⇇ Bᴀᴄᴋ', 'settings#main')])
    await query.message.edit_text(
        text='<b><u>Keywords</u></b>\n\nFile With These Keywords In File Name Will Forwad',
        reply_markup=InlineKeyboardMarkup(btn))
      
  elif type == "rmve_all_keyword":
    await update_configs(user_id, 'keywords', None)
    await query.message.edit_text(text="Successfully Deleted", reply_markup=InlineKeyboardMarkup(buttons))
  elif type.startswith("alert"):
    alert = type.split('_')[1]
    await query.answer(alert, show_alert=True)
      
def main_buttons():
  buttons = [[
       InlineKeyboardButton('⚹ Bᴏᴛꜱ', callback_data=f'settings#bots'),
       InlineKeyboardButton('Cʜᴀɴɴᴇʟꜱ ⚹', callback_data=f'settings#channels')
       ],[
       InlineKeyboardButton('⚹ Cᴀᴩᴛɪᴏɴ', callback_data=f'settings#caption'),
       InlineKeyboardButton('MᴏɴɢᴏDB ⚹', callback_data=f'settings#database')
       ],[
       InlineKeyboardButton('⚹ Fɪʟᴛᴇʀꜱ', callback_data=f'settings#filters'),
       InlineKeyboardButton('Bᴜᴛᴛᴏɴ ⚹', callback_data=f'settings#button')
       ],[
       InlineKeyboardButton('⛭ Exᴛʀꜱ Sᴇᴛᴛɪɴɢꜱ ⛭', callback_data='settings#nextfilters')
       ],[      
       InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data='back')
       ]]
  return InlineKeyboardMarkup(buttons)

def size_limit(limit):
   if str(limit) == "None": return None, ""
   elif str(limit) == "True": return True, "more than"
   else: return False, "less than"

def extract_btn(datas):
    i = 0
    btn = []
    if datas:
       for data in datas:
         if i >= 5: i = 0
         if i == 0: btn.append([InlineKeyboardButton(data, f'settings#alert_{data}')])
         else: btn[-1].append(InlineKeyboardButton(data, f'settings#alert_{data}'))
         i += 1
    return btn 

def size_button(size):
  buttons = [[
       InlineKeyboardButton('+', callback_data=f'settings#update_limit-True-{size}'),
       InlineKeyboardButton('=', callback_data=f'settings#update_limit-None-{size}'),
       InlineKeyboardButton('-', callback_data=f'settings#update_limit-False-{size}')
       ],[
       InlineKeyboardButton('+1', callback_data=f'settings#update_size-{size + 1}'),
       InlineKeyboardButton('-1', callback_data=f'settings#update_size_-{size - 1}')
       ],[
       InlineKeyboardButton('+5', callback_data=f'settings#update_size-{size + 5}'),
       InlineKeyboardButton('-5', callback_data=f'settings#update_size_-{size - 5}')
       ],[
       InlineKeyboardButton('+10', callback_data=f'settings#update_size-{size + 10}'),
       InlineKeyboardButton('-10', callback_data=f'settings#update_size_-{size - 10}')
       ],[
       InlineKeyboardButton('+50', callback_data=f'settings#update_size-{size + 50}'),
       InlineKeyboardButton('-50', callback_data=f'settings#update_size_-{size - 50}')
       ],[
       InlineKeyboardButton('+100', callback_data=f'settings#update_size-{size + 100}'),
       InlineKeyboardButton('-100', callback_data=f'settings#update_size_-{size - 100}')
       ],[
       InlineKeyboardButton('↩ Back', callback_data="settings#main")
     ]]
  return InlineKeyboardMarkup(buttons)
       
async def filters_buttons(user_id):
  filter = await get_configs(user_id)
  filters = filter['filters']
  buttons = [[
       InlineKeyboardButton('🏷️ Fᴏʀᴡᴀʀᴅ Tᴀɢ', callback_data=f'settings_#updatefilter-forward_tag-{filter["forward_tag"]}'),
       InlineKeyboardButton('✅' if filter['forward_tag'] else '❌', callback_data=f'settings#updatefilter-forward_tag-{filter["forward_tag"]}')
       ],[
       InlineKeyboardButton('🖍️ Tᴇxᴛ', callback_data=f'settings_#updatefilter-text-{filters["text"]}'),
       InlineKeyboardButton('✅' if filters['text'] else '❌', callback_data=f'settings#updatefilter-text-{filters["text"]}')
       ],[
       InlineKeyboardButton('📁 Dᴏᴄᴜᴍᴇɴᴛꜱ', callback_data=f'settings_#updatefilter-document-{filters["document"]}'),
       InlineKeyboardButton('✅' if filters['document'] else '❌', callback_data=f'settings#updatefilter-document-{filters["document"]}')
       ],[
       InlineKeyboardButton('🎞️ Vɪᴅᴇᴏꜱ', callback_data=f'settings_#updatefilter-video-{filters["video"]}'),
       InlineKeyboardButton('✅' if filters['video'] else '❌', callback_data=f'settings#updatefilter-video-{filters["video"]}')
       ],[
       InlineKeyboardButton('📷 Pʜᴏᴛᴏꜱ', callback_data=f'settings_#updatefilter-photo-{filters["photo"]}'),
       InlineKeyboardButton('✅' if filters['photo'] else '❌', callback_data=f'settings#updatefilter-photo-{filters["photo"]}')
       ],[
       InlineKeyboardButton('🎧 Aᴜᴅɪᴏ', callback_data=f'settings_#updatefilter-audio-{filters["audio"]}'),
       InlineKeyboardButton('✅' if filters['audio'] else '❌', callback_data=f'settings#updatefilter-audio-{filters["audio"]}')
       ],[
       InlineKeyboardButton('🎤 Vᴏɪᴄᴇ', callback_data=f'settings_#updatefilter-voice-{filters["voice"]}'),
       InlineKeyboardButton('✅' if filters['voice'] else '❌', callback_data=f'settings#updatefilter-voice-{filters["voice"]}')
       ],[
       InlineKeyboardButton('🎭 Aɴɪᴍᴀᴛɪᴏɴ', callback_data=f'settings_#updatefilter-animation-{filters["animation"]}'),
       InlineKeyboardButton('✅' if filters['animation'] else '❌', callback_data=f'settings#updatefilter-animation-{filters["animation"]}')
       ],[
       InlineKeyboardButton('🃏 Sᴛɪᴄᴋᴇʀꜱ', callback_data=f'settings_#updatefilter-sticker-{filters["sticker"]}'),
       InlineKeyboardButton('✅' if filters['sticker'] else '❌', callback_data=f'settings#updatefilter-sticker-{filters["sticker"]}')
       ],[
       InlineKeyboardButton('▶️ Sᴋɪᴩ Dᴜᴩʟɪᴄᴀᴛᴇ', callback_data=f'settings_#updatefilter-duplicate-{filter["duplicate"]}'),
       InlineKeyboardButton('✅' if filter['duplicate'] else '❌', callback_data=f'settings#updatefilter-duplicate-{filter["duplicate"]}')
       ],[
       InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons) 

async def next_filters_buttons(user_id):
  filter = await get_configs(user_id)
  filters = filter['filters']
  buttons = [[
       InlineKeyboardButton('📊 Pᴏʟʟ', callback_data=f'settings_#updatefilter-poll-{filters["poll"]}'),
       InlineKeyboardButton('✅' if filters['poll'] else '❌', callback_data=f'settings#updatefilter-poll-{filters["poll"]}')
       ],[
       InlineKeyboardButton('🔒 Sᴇᴄᴜʀᴇ Mᴇꜱꜱᴀɢᴇ', callback_data=f'settings_#updatefilter-protect-{filter["protect"]}'),
       InlineKeyboardButton('✅' if filter['protect'] else '❌', callback_data=f'settings#updatefilter-protect-{filter["protect"]}')
       ],[
       InlineKeyboardButton('🛑 Sɪᴢᴇ Lɪᴍɪᴛ', callback_data='settings#file_size')
       ],[
       InlineKeyboardButton('💾 Exᴛᴇɴꜱɪᴏɴ', callback_data='settings#get_extension')
       ],[
       InlineKeyboardButton('📌 Kᴇʏᴡᴏʀᴅꜱ', callback_data='settings#get_keyword')
       ],[
       InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons)
