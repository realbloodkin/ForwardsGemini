
from pyrogram.errors import UserNotParticipant
import re, asyncio
from database import db
from config import temp
from .public import SYD_CHANNELS
from .test import CLIENT , start_clone_bot
from translation import Translation
from pyrogram import Client, filters 
#from pyropatch.utils import unpack_new_file_id
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()
COMPLETED_BTN = InlineKeyboardMarkup(
   [
      [InlineKeyboardButton('Placeholder', url='https://t.me/partDevil')],
      [InlineKeyboardButton('Placeholder', url='https://t.me/partDevil')]
   ]
)

CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton('⛒ Cᴀɴᴄᴇʟ ⛒', 'terminate_frwd')]])





@Client.on_message(filters.command("unequify") & filters.private)
async def unequify(client, message):
   user_id = message.from_user.id
   temp.CANCEL[user_id] = False
   if temp.lock.get(user_id) and str(temp.lock.get(user_id))=="True":
      return await message.reply("Pʟᴇᴀꜱᴇ Wᴀɪᴛ Uɴᴛɪʟ Pʀᴇᴠɪᴏᴜꜱ Tᴀꜱᴋ Iꜱ Cᴏᴍᴩʟᴇᴛᴇᴅ")
   _bot = await db.get_bot(user_id)
   if not _bot or _bot['is_bot']:
      return await message.reply("Nᴇᴇᴅ UꜱᴇʀBᴏᴛ To Foʀ Tʜɪꜱ Pʀᴏᴄᴇꜱꜱ. Pʟᴇᴀꜱᴇ Aᴅᴅ A UꜱᴇʀBᴏᴛ Uꜱɪɴɢ /settings")
   for channel in SYD_CHANNELS:
        try:
            user = await bot.get_chat_member(channel, message.from_user.id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
            
   if not_joined_channels:
       buttons = [
           [
               InlineKeyboardButton(
                   text=f"✧ Jᴏɪɴ {channel.capitalize().replace("_", " ")}✧", url=f"https://t.me/{channel}"
               )
           ]
       for channel in not_joined_channels
       ]
       buttons.append(
           [
               InlineKeyboardButton(
                   text="✧ Jᴏɪɴ Bᴀᴄᴋ Uᴩ ✧", url="https://t.me/norFederation"

               )
           ]
       )
       buttons.append(
           [
               InlineKeyboardButton(
                   text="☑ ᴊᴏɪɴᴇᴅ ☑", callback_data="check_subscription"
               )
           ]
       )

       text = "**Sᴏʀʀʏ, ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ɪɴ ᴏᴜʀ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ, ᴩʟᴇᴀꜱᴇ ᴅᴏ ꜱᴏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.. ⚡ .**"
       return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        
   target = await client.ask(user_id, text="Forward The Last Message From Target Chat Or Send Last Message Link.\n/cancel - To Cancel This Process")
   if target.text.startswith("/"):
      return await message.reply("Process Cancelled !")
   elif target.text:
      regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
      match = regex.match(target.text.replace("?single", ""))
      if not match:
         return await message.reply('Iɴᴠᴀʟɪᴅ Lɪɴᴋ !')
      chat_id = match.group(4)
      last_msg_id = int(match.group(5))
      if chat_id.isnumeric():
         chat_id  = int(("-100" + chat_id))
   elif fromid.forward_from_chat.type in ['channel', 'supergroup']:
        last_msg_id = target.forward_from_message_id
        chat_id = target.forward_from_chat.username or target.forward_from_chat.id
   else:
        return await message.reply_text("Iɴᴠᴀʟɪᴅ !")
   confirm = await client.ask(user_id, text="Sᴇɴᴅ /yes To Sᴛᴀʀᴛ Tʜᴇ Pʀᴏᴄᴇꜱꜱ Aɴᴅ /no To Cᴀɴᴄᴇʟ Tʜɪꜱ Pʀᴏᴄᴇꜱꜱ!")
   if confirm.text.lower() == '/no':
      return await confirm.reply("Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !")
   sts = await confirm.reply("Pʀᴏᴄᴇꜱꜱɪɴɢ...")
   try:
      bot = await start_clone_bot(CLIENT.client(_bot))
   except Exception as e:
      return await sts.edit(e)
   try:
       k = await bot.send_message(chat_id, text="Tᴇꜱᴛɪɴɢ")
       await k.delete()
   except:
       await sts.edit(f"Please Make Your [Userbot](t.me/{_bot['username']}) Admin In Target Chat With Full Permissions")
       return await bot.stop()
   MESSAGES = []
   DUPLICATE = []
   total=deleted=0
   temp.lock[user_id] = True
   try:
     await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Progressing"), reply_markup=CANCEL_BTN)
     async for message in bot.search_messages(chat_id=chat_id, filter="document"):
        if temp.CANCEL.get(user_id) == True:
           await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Cancelled"), reply_markup=COMPLETED_BTN)
           return await bot.stop()
        file = message.document
        file_id = unpack_new_file_id(file.file_id) 
        if file_id in MESSAGES:
           DUPLICATE.append(message.id)
        else:
           MESSAGES.append(file_id)
        total += 1
        if total %10000 == 0:
           await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Progressing"), reply_markup=CANCEL_BTN)
        if len(DUPLICATE) >= 100:
           await bot.delete_messages(chat_id, DUPLICATE)
           deleted += 100
           await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Cancelled"), reply_markup=CANCEL_BTN)
           DUPLICATE = []
     if DUPLICATE:
        await bot.delete_messages(chat_id, DUPLICATE)
        deleted += len(DUPLICATE)
   except Exception as e:
       temp.lock[user_id] = False 
       await sts.edit(f"**Error**\n\n`{e}`")
       return await bot.stop()
   temp.lock[user_id] = False
   await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Completed"), reply_markup=COMPLETED_BTN)
   await bot.stop()
   

