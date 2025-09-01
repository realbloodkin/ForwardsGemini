from pyrogram import Client, filters
from pyrogram.types import Message
import logging
import asyncio

# Set up logging
LOGGER = logging.getLogger(__name__)

@Client.on_message(filters.command("unequify"))
async def unequify_command(client: Client, message: Message):
    """
    Finds and deletes duplicate media files in a chat using Pyrogram.
    """
    # A set to store the unique IDs of files we have already seen
    seen_files = set()
    # A list to store the message IDs of duplicates to be deleted
    messages_to_delete = []

    try:
        await message.reply_text("✅ **Starting Scan...**\n\nI will now check for duplicate files. This may take a moment.")
    except Exception as e:
        LOGGER.error(f"Could not send initial reply in chat {message.chat.id}: {e}")
        return

    try:
        # Iterate through the chat history using the Pyrogram client
        async for msg in client.iter_history(message.chat.id):
            file_id = None
            
            if msg.document:
                file_id = msg.document.file_unique_id
            elif msg.video:
                file_id = msg.video.file_unique_id
            elif msg.audio:
                file_id = msg.audio.file_unique_id
            
            if file_id:
                if file_id in seen_files:
                    messages_to_delete.append(msg.message_id)
                else:
                    seen_files.add(file_id)

        # Bulk delete all the duplicates we found
        if messages_to_delete:
            await client.send_message(message.chat.id, f"Found and deleting {len(messages_to_delete)} duplicate files.")
            
            # Pyrogram can delete up to 100 messages at once
            for i in range(0, len(messages_to_delete), 100):
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=messages_to_delete[i:i + 100]
                )
                await asyncio.sleep(1) # Pause briefly to avoid rate limits
                
            await client.send_message(message.chat.id, "✅ **Cleanup Complete!**")
        else:
            await client.send_message(message.chat.id, "✅ No duplicate files were found.")
            
    except Exception as e:
        LOGGER.error(f"A critical error occurred during the unequify scan in chat {message.chat.id}: {e}")
        await client.send_message(message.chat.id, "❌ **Error!** An unexpected error occurred. Please check the logs for details.")

