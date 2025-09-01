from bot import bot, db, user
from telebot.types import Message
import time
import logging

# Set up a logger for better debugging
LOGGER = logging.getLogger(__name__)

@bot.message_handler(commands=['unequify'])
def unequify_command(message: Message):
    """
    Finds and deletes duplicate media files (documents, videos, audio) in a chat.
    """
    # A set to store the file_unique_id of files we have already seen
    seen_files = set()
    # A list to store the message IDs of duplicate messages to be deleted
    messages_to_delete = []

    try:
        # Inform the user that the process has started
        bot.reply_to(message, "✅ **Starting Scan...**\n\nI will now check for duplicate files in this channel. This may take a moment.")
    except Exception as e:
        LOGGER.error(f"Could not send initial reply in chat {message.chat.id}: {e}")
        return

    try:
        # Iterate through all messages in the channel using the Pyrogram client ('user')
        for msg in user.iter_history(message.chat.id):
            file_id = None
            
            # Check for different media types and get their unique file ID
            if msg.document:
                file_id = msg.document.file_unique_id
            elif msg.video:
                file_id = msg.video.file_unique_id
            elif msg.audio:
                file_id = msg.audio.file_unique_id
            
            # If the message contains a file we can check
            if file_id:
                # If we have seen this file before, it's a duplicate
                if file_id in seen_files:
                    messages_to_delete.append(msg.message_id)
                else:
                    # If it's the first time we've seen this file, add it to our set
                    seen_files.add(file_id)

        # Now, delete all the duplicate messages we found
        if messages_to_delete:
            bot.send_message(message.chat.id, f"Found and deleting {len(messages_to_delete)} duplicate files.")
            for msg_id in messages_to_delete:
                try:
                    # Use the correct 'bot' object (pyTelegramBotAPI) to delete messages
                    bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                    time.sleep(1) # Add a small delay to avoid hitting Telegram's rate limits
                except Exception as e:
                    # Log errors if a message can't be deleted (e.g., too old, no permissions)
                    LOGGER.warning(f"Could not delete message {msg_id} in chat {message.chat.id}: {e}")
            bot.send_message(message.chat.id, "✅ **Cleanup Complete!**")
        else:
            bot.send_message(message.chat.id, "✅ No duplicate files were found.")
            
    except Exception as e:
        LOGGER.error(f"A critical error occurred during the unequify scan in chat {message.chat.id}: {e}")
        bot.send_message(message.chat.id, "❌ **Error!** An unexpected error occurred while scanning the chat. Please check the logs.")

