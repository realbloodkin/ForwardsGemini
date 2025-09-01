from bot import bot, db, user
from telebot.types import Message
import logging

LOGGER = logging.getLogger(__name__)

@bot.message_handler(commands=['unequify'])
def unequify_command(message: Message):
    chat_id_to_scan = message.chat.id
    bot.reply_to(message, f"Attempting to scan chat ID: {chat_id_to_scan}. Check the logs for details.")
    
    try:
        LOGGER.info(f"--- STARTING UNEQUIFY DIAGNOSTIC FOR CHAT {chat_id_to_scan} ---")
        
        # We will try to get just ONE message to see if history access is working.
        # The 'limit=1' makes it fast.
        history = user.get_chat_history(chat_id_to_scan, limit=1)
        
        message_found = False
        for msg in history:
            # If this loop runs, it means we found at least one message.
            LOGGER.info(f"SUCCESS! Found message: {msg.text[:50]}...") # Print first 50 chars of the message text
            message_found = True
            
        if message_found:
            bot.send_message(chat_id_to_scan, "✅ Diagnostic PASSED. The user client can successfully read this chat's history.")
        else:
            bot.send_message(chat_id_to_scan, "❌ Diagnostic FAILED. The user client could not find any messages. The chat might be empty or inaccessible.")

    except Exception as e:
        # If this 'except' block is triggered, there is a serious error.
        LOGGER.error(f"CRITICAL ERROR during diagnostic: {e}", exc_info=True)
        bot.send_message(chat_id_to_scan, f"❌ Diagnostic FAILED with a critical error. Check the logs for an exception like: {e}")

    LOGGER.info(f"--- UNEQUIFY DIAGNOSTIC COMPLETE ---")
