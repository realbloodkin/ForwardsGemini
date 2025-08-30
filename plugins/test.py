
import os
import re 
import sys
import typing
import asyncio 
import logging 
from database import db 
from config import Config, temp
from pyrogram import Client, filters
from pyrogram.raw.all import layer
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.errors import FloodWait
from config import Config
from translation import Translation

from typing import Union, Optional, AsyncGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:/{0,2}(.+?)(:same)?])")
BOT_TOKEN_TEXT = "1) Cʀᴇᴀᴛᴇ A Bᴏᴛ Uꜱɪɴɢ @BotFather [ꜱᴇɴᴅ <code>/newbot</code> ᴛᴏ ʙᴏᴛ ꜰᴀᴛʜᴇʀ ᴀɴᴅ ᴛʜᴇ ɴᴀᴍᴇ ᴀɴᴅ ᴜꜱᴇʀɴᴀᴍᴇ ʀᴇꜱᴩᴇᴄᴛɪᴠᴇʟʏ]\n\n2) Tʜᴇɴ Yᴏᴜ Wɪʟʟ Gᴇᴛ A Mᴇꜱꜱᴀɢᴇ Wɪᴛʜ Bᴏᴛ Tᴏᴋᴇɴ\n\n3) Fᴏʀᴡᴀʀᴅ Tʜᴀᴛ Mᴇꜱꜱᴀɢᴇ Tᴏ Mᴇ \n\nIꜰ Yᴏᴜ Hᴀᴠᴇ A Bᴏᴛ Aʟʀᴇᴀᴅʏ, Yᴏᴜ Cᴀɴ Fᴏʀᴡᴀʀᴅ Iᴛꜱ Tᴏᴋᴇɴ Fʀᴏᴍ API Bᴏᴛ Tᴏᴋᴇɴ."
SESSION_STRING_SIZE = 351



async def start_clone_bot(FwdBot, data=None):
   await FwdBot.start()
   #
   async def iter_messages(
      self, 
      chat_id: Union[int, str], 
      limit: int, 
      offset: int = 0,
      search: str = None,
      filter: "types.TypeMessagesFilter" = None,
      ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
   #
   FwdBot.iter_messages = iter_messages
   return FwdBot



class CLIENT: 
  def __init__(self):
     self.api_id = Config.API_ID
     self.api_hash = Config.API_HASH
    
  def client(self, data, user=None):
     if user == None and data.get('is_bot') == False:
        return Client("USERBOT", self.api_id, self.api_hash, session_string=data.get('session'))
     elif user == True:
        return Client("USERBOT", self.api_id, self.api_hash, session_string=data)
     elif user != False:
        data = data.get('token')
     return Client("BOT", self.api_id, self.api_hash, bot_token=data, in_memory=True)
  


  async def add_bot(self, bot, message):
     user_id = int(message.from_user.id)
     msg = await bot.ask(chat_id=user_id, text=BOT_TOKEN_TEXT)
     if msg.text=='/cancel':
        return await msg.reply('<b>Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !</b>')
     elif not msg.forward_date:
       return await msg.reply_text("Tʜɪꜱ Iꜱ Nᴏᴛ Fᴏʀᴡᴀʀᴅᴇᴅ Mᴇꜱꜱᴀɢᴇ !")
     elif str(msg.forward_from.id) != "93372553":
       return await msg.reply_text("Tʜɪꜱ Mᴇꜱꜱᴀɢᴇ Wᴀꜱ Nᴏᴛ Fᴏʀᴡᴀʀᴅᴇᴅ Fʀᴏᴍ Tʜᴇ Bᴏᴛ Fᴀᴛʜᴇʀ !")
     bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', msg.text, re.IGNORECASE)
     bot_token = bot_token[0] if bot_token else None
     if not bot_token:
       return await msg.reply_text("Tʜᴇʀᴇ Iꜱ No Bᴏᴛ Tᴏᴋᴇɴ Iɴ Tʜᴀᴛ Mᴇꜱꜱᴀɢᴇ !Tʀʏ Aɢᴀɪɴ Pʟᴇᴀꜱᴇ !")
     try:
       _client = await start_clone_bot(self.client(bot_token, False), True)
     except Exception as e:
       await msg.reply_text(f"Bot Error :</b> `{e}` /nFᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ @Syd_Xyz Iꜰ ʏᴏᴜ ɴᴇᴇᴅ HELP !")
     _bot = _client.me
     details = {
       'id': _bot.id,
       'is_bot': True,
       'user_id': user_id,
       'name': _bot.first_name,
       'token': bot_token,
       'username': _bot.username 
     }
     await db.add_bot(details)
     return True
    


  async def add_session(self, bot, message):
     user_id = int(message.from_user.id)
     text = "<b>⚠️ Dɪꜱᴄʟᴀɪᴍᴇʀ ⚠️</b>\n\nYᴏᴜ Cᴀɴ Uꜱᴇ Yoᴜʀ Sᴇꜱꜱɪᴏɴ Fᴏʀ Fᴏʀᴡᴀʀᴅɪɴɢ Mᴇꜱꜱᴀɢᴇ Fʀᴏᴍ Pʀɪᴠᴀᴛᴇ Cʜᴀᴛ Tᴏ Aɴᴏᴛʜᴇʀ Cʜᴀᴛ.\nPʟᴇᴀꜱᴇ Aᴅᴅ Yᴏᴜʀ <b><u>Pʏʀᴏɢʀᴀᴍ Sᴇꜱꜱɪᴏɴ</u> Wɪᴛʜ Yᴏᴜʀ Oᴡɴ Rɪꜱᴋ </b>. Tʜᴇʀᴇ Iꜱ A Cʜᴀɴᴄᴇ Tᴏ Bᴀɴ Yᴏᴜʀ Aᴄᴄᴏᴜɴᴛ (ꜱᴏ, ꜰᴏᴡᴀʀᴅɪɴɢ ᴡɪʟʟ ʙᴇ ʟɪɪᴛʟᴇ ꜱʟᴏᴡ). Mʏ Dᴇᴠᴇʟᴏᴩᴇʀ <b>Iꜱ Nᴏᴛ Rᴇꜱᴩᴏɴꜱɪʙʟᴇ Iꜰ Yᴏᴜʀ Aᴄᴄᴏᴜɴᴛ Mᴀʏ Gᴇᴛ Bᴀɴɴᴇᴅ! /nUSE THE ACCOUNT WITH WHICH YOU CAN RISK(NOT IMPORTANT).</b>"
     await bot.send_message(user_id, text=text)
     msg = await bot.ask(chat_id=user_id, text="<b>Send your pyrogram session.\nget it from @mdsessiongenbot\n\n/cancel - cancel the process</b>")
     if msg.text=='/cancel':
        return await msg.reply('<b>Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ !</b>')
     elif len(msg.text) < SESSION_STRING_SIZE:
        return await msg.reply('Iɴᴠᴀʟɪᴅ Sᴇꜱꜱɪᴏɴ Sᴛʀɪɴɢ !')
     try:
       client = await start_clone_bot(self.client(msg.text, True), True)
     except Exception as e:
       await msg.reply_text(f"<b>User Bot Error :</b> `{e}` /nFᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ @Syd_Xyz Iꜰ ʏᴏᴜ ɴᴇᴇᴅ HELP !")
     user = client.me
     details = {
       'id': user.id,
       'is_bot': False,
       'user_id': user_id,
       'name': user.first_name,
       'session': msg.text,
       'username': user.username
     }
     await db.add_bot(details)
     return True
    





@Client.on_message(filters.private & filters.command('reset'))
async def forward_tag(bot, m):
    default = await db.get_configs("01")
    temp.CONFIGS[m.from_user.id] = default
    await db.update_configs(m.from_user.id, default)
    await m.reply("Successfully Settings Reseted ✔️")




@Client.on_message(filters.command('resetall') & filters.user(Config.OWNER_ID))
async def resetall(bot, message):
  users = await db.get_all_users()
  sts = await message.reply("Processing")
  TEXT = "Total: {}\nSuccess: {}\nFailed: {}\nExcept: {}"
  total = success = failed = already = 0
  ERRORS = []
  async for user in users:
      user_id = user['id']
      default = await get_configs(user_id)
      default['db_uri'] = None
      total += 1
      if total %10 == 0:
         await sts.edit(TEXT.format(total, success, failed, already))
      try: 
         await db.update_configs(user_id, default)
         success += 1
      except Exception as e:
         ERRORS.append(e)
         failed += 1
  if ERRORS:
     await message.reply(ERRORS[:100])
  await sts.edit("Completed\n" + TEXT.format(total, success, failed, already))
  


async def get_configs(user_id):
  #configs = temp.CONFIGS.get(user_id)
  #if not configs:
  configs = await db.get_configs(user_id)
  #temp.CONFIGS[user_id] = configs 
  return configs



async def update_configs(user_id, key, value):
  current = await db.get_configs(user_id)
  if key in ['caption', 'duplicate', 'db_uri', 'forward_tag', 'protect', 'file_size', 'size_limit', 'extension', 'keywords', 'button']:
     current[key] = value
  else: 
     current['filters'][key] = value
 # temp.CONFIGS[user_id] = value
  await db.update_configs(user_id, current)
    

def parse_buttons(text, markup=True):
    buttons = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            if bool(match.group(4)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(3).replace(" ", "")))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(3).replace(" ", ""))])
    if markup and buttons:
       buttons = InlineKeyboardMarkup(buttons)
    return buttons if buttons else None


