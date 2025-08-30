# MrSyD
# Telegram Channel @Bot_Cracker
# Developer @syd_xyz




import os
from config import Config

class Translation(object):
  START_TXT = """Hᴇʏ {}

<i>ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀᴜᴛᴏ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ
ɪ ᴄᴀɴ ғᴏʀᴡᴀʀᴅ ᴀʟʟ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴏɴᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ғᴇᴀᴛᴜʀᴇs.</i>

<b>Cʟɪᴄᴋ Hᴇʟᴘ Fᴏʀ Kɴᴏᴡ Mᴇ</b>"""


  HELP_TXT = """<b><u>⋈ Hᴇʟᴩ</b></u>

<b><u>≍ Aᴠᴀɪʟᴀʙʟᴇ Cᴏᴍᴍᴀɴᴅꜱ :</u></b>
⏣ __/start - Cʜᴇᴄᴋ I'ᴍ Aʟɪᴠᴇ__ 
⏣ __/forward - Fᴏʀᴡᴀʀᴅ Mᴇꜱꜱᴀɢᴇꜱ__
⏣ __/unequify - Dᴇʟᴇᴛᴇ Dᴜᴩʟɪᴄᴀᴛᴇ Mᴇꜱꜱᴀɢᴇꜱ Iɴ Cʜᴀɴɴᴇʟꜱ__
⏣ __/settings - Cᴏɴꜰɪɢᴜʀᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ__
⏣ __/reset - Rᴇꜱᴇᴛ Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ__

<b><u>≬≬ Fᴇᴀᴛᴜʀᴇꜱ :</b></u>
► __Fᴏʀᴡᴀʀᴅ Mᴇꜱꜱᴀɢᴇ Fʀᴏᴍ Pᴜʙʟɪᴄ Cʜᴀɴɴᴇʟ To Yᴏᴜʀ Cʜᴀɴɴᴇʟ Wɪᴛʜᴏᴜᴛ Aᴅᴍɪɴ Peᴇʀᴍɪꜱꜱɪᴏɴ. Iꜰ Tʜᴇ Cʜᴀɴɴᴇʟ Iꜱ Pʀɪᴠᴀᴛᴇ Nᴇᴇᴅ Aᴅᴍɪɴ Pᴇʀᴍɪꜱꜱɪᴏɴ, Bᴇᴛᴇʀ Tᴏ Uꜱᴇ UꜱᴇʀBᴏᴛ__
► __Forward Message Fʀᴏᴍ Private Cʜᴀɴɴᴇʟ To Yᴏᴜʀ Cʜᴀɴɴᴇʟ Bʏ Uꜱɪɴɢ UꜱᴇʀBᴏᴛ (Uꜱᴇʀ Mᴜꜱᴛ Bᴇ Mᴇᴍʙᴇʀ Iɴ Tʜᴇʀᴇ)__
► __Cᴜꜱᴛᴏᴍ Cᴀᴩᴛɪᴏɴ__
► __Cᴜꜱᴛᴏᴍ Bᴜᴛᴛᴏɴ__
► __Sᴜᴩᴩᴏʀᴛ Rᴇꜱᴛʀɪᴄᴛᴇᴅ Cʜᴀᴛꜱ__
► __Sᴋɪᴩ Dᴜᴩʟɪᴄᴀᴛᴇ Mᴇꜱꜱᴀɢᴇꜱ__
► __Fɪʟᴛᴇʀ Tʏᴩᴇ Oꜰ Mᴇꜱꜱᴀɢᴇꜱ__
► __Sᴋɪᴩ Mᴇꜱꜱᴀɢᴇꜱ Bᴀꜱᴇᴅ Oɴ Exᴛᴇɴꜱɪᴏɴꜱ & Kᴇʏᴡᴏʀᴅ & Sɪᴢᴇ__
"""
  
  HOW_USE_TXT = """<b><u>⚠️ Bᴇꜰᴏʀᴇ Fᴏʀᴡᴀʀᴅ :</b></u>
  
► __Aᴅᴅ A Bᴏᴛ Oʀ Uꜱᴇʀʙᴏᴛ__
► __Aᴅᴅ Aᴛʟᴇᴀꜱᴛ Oɴᴇ Cʜᴀᴛ Tᴏ Cʜᴀɴɴᴇʟꜱ (Yᴏᴜʀ Bᴏᴛ/UꜱᴇʀBᴏᴛ Mᴜꜱᴛ Bᴇ Aᴅᴍɪɴ Tʜᴇʀᴇ)__
► __Yᴏᴜ Cᴀɴ Aᴅᴅ Cʜᴀᴛꜱ Oʀ Bᴏᴛꜱ Bʏ Uꜱɪɴɢ /settings__
► __Iꜰ Tʜᴇ **Fʀᴏᴍ Cʜᴀɴɴᴇʟ** Iꜱ Pʀɪᴠᴀᴛᴇ, Yᴏᴜʀ UꜱᴇʀBᴏᴛ Mᴜꜱᴛ Bᴇ A Mᴇᴍʙᴇʀ Iɴ Tʜᴇʀᴇ Oʀ Yᴏᴜʀ Bᴏᴛ Mᴜꜱᴛ Nᴇᴇᴅ Tᴏ Bᴇ Aᴅᴍɪɴ Iɴ Tʜᴇʀᴇ Aʟꜱᴏ__
► __Tʜᴇɴ Uꜱᴇ /forward Tᴏ Fᴏʀᴡᴀʀᴅ Mᴇꜱꜱᴀɢᴇꜱ, Wʜᴇʀᴇ Iᴛ Aꜱᴋ Fᴏʀ Sᴏᴜʀᴄᴇ Cʜᴀᴛ Tᴏ Fᴏᴡᴀʀᴅ__"""
  
  ABOUT_TXT = """<b>⋉ Mʏ Nᴀᴍᴇ :</b> {}
<b>⋉ Lᴀɴɢᴜᴀɢᴇ :</b> <a href='https://t.me/+0Zi1FC4ulo8zYzVl'>Sᴀᴍᴇ ᴀꜱ!</a>
<b>⋉ Lɪʙʀᴀʀʏ :</b> <a href='https://t.me/nt_Backup'>Bᴀᴄᴋ-Uᴩ 🕯️</a>
<b>⋉ Sᴇʀᴠᴇʀ :</b> <a href='https://t.me/+7P5-bLWSuPA5NmFl'>TG 🪄</a>
<b>⋉ Cʜᴀɴɴᴇʟ :</b> <a href='https://t.me/Bot_Cracker'>Bᴏᴛ Cʀᴀᴄᴋᴇʀ 🎶</a>
<b>⋉ Dᴇᴠᴇʟᴏᴩᴇʀ :</b> <a href='https://t.me/Syd_XyZ'>ᴍʀ. ꜱʏᴅ 🌧️</a>"""
  
  STATUS_TXT = """<b><u>Bᴏᴛ Sᴛᴀᴛᴜꜱ:</u></b>
  
<b>⊛ Tᴏᴛᴀʟ Uꜱᴇʀꜱ :</b> <code>{}</code>
<b>⚝ Tᴏᴛᴀʟ Bᴏᴛꜱ :</b> <code>{}</code>
<b>❉ Fᴏʀᴡᴀʀᴅɪɴɢ :</b> <code>{}</code>
"""
  
  FROM_MSG = "<b><u>Sᴇᴛ Sᴏᴜʀᴄᴇ Cʜᴀᴛ</></>\n\nForward The Last Mᴇꜱꜱᴀɢᴇ Or Last Mᴇꜱꜱᴀɢᴇ Lɪɴᴋ Oꜰ Sᴏᴜʀᴄᴇ Cʜᴀᴛ.\n/cancel - Tᴏ Cᴀɴᴄᴇʟ Tʜɪꜱ Pʀᴏᴄᴇꜱꜱ"
  TO_MSG = "<b><u>Cʜᴏᴏꜱᴇ Tᴀʀɢᴇᴛ Cʜᴀᴛ</u></b>\n\nCʜᴏᴏꜱᴇ Yᴏᴜʀ Tᴀʀɢᴇᴛ Cʜᴀᴛ Fʀᴏᴍ Tʜᴇ Gɪᴠᴇɴ Bᴜᴛᴛᴏɴꜱ.\n/cancel - Tᴏ Cᴀɴᴄᴇʟ Tʜɪꜱ Pʀᴏᴄᴇꜱꜱ"
  SKIP_MSG = "<b><u>Sᴇᴛ Mᴇꜱꜱᴀɢᴇ Sᴋɪᴩᴩɪɴɢ Nᴜᴍʙᴇʀ</u></b>\n\nSᴋɪᴩ Tʜᴇ Mᴇꜱꜱᴀɢᴇ Aꜱ Mᴜᴄʜ Aꜱ Yᴏᴜ Eɴᴛᴇʀ Tʜᴇ Nᴜᴍʙᴇʀ Aɴᴅ Tʜᴇ Rᴇꜱᴛ Oꜰ Tʜᴇ Mᴇꜱꜱᴀɢᴇ Wɪʟʟ Bᴇ Fᴏʀᴡᴀʀᴅ\nDᴇꜰᴀᴜʟᴛ Sᴋɪᴩ Nᴜᴍʙᴇʀ = <code>0</code>\n<code>eg: Iꜰ Yᴏᴜ Eɴᴛᴇʀ 0, 0 Mᴇꜱꜱᴀɢᴇ Sᴋɪᴩᴩᴇᴅ\nYᴏᴜ Eɴᴛᴇʀ 5 = 5 Mᴇꜱꜱᴀɢᴇ Sᴋɪᴩᴩᴇᴅ</code>\nSᴇɴᴅ Zᴇʀᴏ(0) Tᴏ Aᴠᴏɪᴅ Sᴋɪᴩᴩɪɴɢ\n/cancel - Tᴏ Cᴀɴᴄᴇʟ Tʜɪꜱ Pʀᴏᴄᴇꜱꜱ"
  CANCEL = "<b> Pʀᴏᴄᴇꜱꜱ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ! </b>"
  BOT_DETAILS = "<b><u>📄 Bᴏᴛ Dᴇᴛᴀɪʟꜱ</u></b>\n\n<b>➣ Nᴀᴍᴇ :</b> <code>{}</code>\n<b>➣ Bᴏᴛ ID :</b> <code>{}</code>\n<b>➣ Uꜱᴇʀɴᴀᴍᴇ :</b> @{}"
  USER_DETAILS = "<b><u>📄 UꜱᴇʀBᴏᴛ Dᴇᴛᴀɪʟꜱ</u></b>\n\n<b>➣ Nᴀᴍᴇ :</b> <code>{}</code>\n<b>➣ Uꜱᴇʀ ID :</b> <code>{}</code>\n<b>➣ Uꜱᴇʀɴᴀᴍᴇ :</b> @{}"  
         
  TEXT = """<b><u>Fᴏʀᴡᴀʀᴅ Sᴛᴀᴛᴜꜱ</u></b>
  
<b>🕵 Fᴇᴛᴄʜᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>✅ Sᴜᴄᴄᴇꜱꜰᴜʟʟʏ Fᴏʀᴡᴀʀᴅ :</b> <code>{}</code>
<b>👥 Dᴜʙʟɪᴄᴀᴛᴇ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>🗑 Dᴇʟᴇᴛᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>🪆 Sᴋɪᴩᴩᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>🔁 Fɪʟᴛᴇʀᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>📊 Cᴜʀʀᴇɴᴛ Sᴛᴀᴛᴜꜱ :</b> <code>{}</code>
<b>🔥 Pᴇʀᴄᴇɴᴛᴀɢᴇ :</b> <code>{}</code> %

{}
"""

  TEXT1 = """<b><u>Fᴏʀᴡᴀʀᴅ Sᴛᴀᴛᴜꜱ</u></b>

<b>🕵 Fᴇᴛᴄʜᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>✅ Sᴜᴄᴄᴇꜱꜰᴜʟʟʏ Fᴏʀᴡᴀʀᴅ :</b> <code>{}</code>
<b>👥 Dᴜʙʟɪᴄᴀᴛᴇ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>🗑 Dᴇʟᴇᴛᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>🪆 Sᴋɪᴩᴩᴇᴅ Mᴇꜱꜱᴀɢᴇ :</b> <code>{}</code>
<b>📊 Sᴛᴀᴛꜱ :</b> <code>{}</code>
<b>⏳ Pʀᴏɢʀᴇꜱꜱ :</b> <code>{}</code>
<b>⏰ Eᴛᴀ :</b> <code>{}</code>
{}"""

  DUPLICATE_TEXT = """<b><u>UɴᴇQᴜɪꜰʏ Sᴛᴀᴛᴜꜱ</u></b>

<b>🕵 Fᴇᴛᴄʜᴇᴅ Fɪʟᴇꜱ :</b> <code>{}</code>

<b>👥 Dᴜʙʟɪᴄᴀᴛᴇ Dᴇʟᴇᴛᴇᴅ :</b> <code>{}</code>

{}
"""
  DOUBLE_CHECK = """<b><u>Dᴏᴜʙʟᴇ Cʜᴇᴄᴋɪɴɢ</u></b>
  
Bᴇꜰᴏʀ Fᴏʀᴡᴀʀᴅɪɴɢ Tʜᴇ Mᴇꜱꜱᴀɢᴇꜱ Cʟɪᴄᴋ Tʜᴇ Yᴇꜱ Bᴜᴛᴛᴏɴ Oɴʟʏ Aꜰᴛᴇʀ Cʜᴇᴄᴋɪɴɢ Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ

<b>★ Yᴏᴜʀ Bᴏᴛ :</b> [{botname}](t.me/{botuname})
<b>★ Fʀᴏᴍ Cʜᴀɴɴᴇʟ :</b> <code>{from_chat}<>
<b>★ Tᴏ Cʜᴀɴɴᴇʟ :</b> <code>{to_chat}</code>
<b>★ Sᴋɪᴩ Mᴇꜱꜱᴀɢᴇꜱ :</b> <code>{skip}</code>

<i>° [{botname}](t.me/{botuname}) Mᴜꜱᴛ Bᴇ Aᴅᴍɪɴ Iɴ <b>Tᴀʀɢᴇᴛ Cʜᴀᴛ</b></i> (<code>{to_chat}</code>)
<i>° Iꜰ Tʜᴇ <b>Sᴏᴜʀᴄᴇ Cʜᴀᴛ</b> Iꜱ Pʀɪᴠᴀᴛᴇ Yᴏᴜʀ Userbot Mᴜꜱᴛ Bᴇ Mᴇᴍʙᴇʀ Or Yᴏᴜʀ Bᴏᴛ Mᴜꜱᴛ Bᴇ Aᴅᴍɪɴ Iɴ Tʜᴇʀᴇ Aʟꜱᴏ</i>

<b>Iꜰ Tʜᴇ Aʙᴏᴠᴇ Iꜱ Cʜᴇᴄᴋᴇᴅ Tʜᴇɴ Tʜᴇ Yᴇꜱ Bᴜᴛᴛᴏɴ Cᴀɴ Bᴇ Cʟɪᴄᴋᴇᴅ</b>"""










# MrSyD
# Telegram Channel @Bot_Cracker
# Developer @syd_xyz
