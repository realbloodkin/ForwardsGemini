from pyrogram import filters
from pyrogram.types import Message
import logging
import asyncio

# Set up logging
LOGGER = logging.getLogger(__name__)

# NOTE: We are NOT importing 'bot' or 'user' at the top of the file anymore.

# **CRITICAL FIX:** The decorator must be directly above the function definition.
@filters.command("unequify")
async def unequify_command(client, message: Message):
    """
    Finds and deletes duplicate media files in a chat.
    Lazily imports the 'user' client to avoid circular dependency.
    """
    # **LAZY IMPORT:** Import the 'user' client here, only when the command is run.
    from bot import user

    seen_files = set()
    messages_to_delete = []

    try:
        # Use the 'client' object (which is the bot) to reply
        await message.reply_text("✅ **Starting Scan...**\n\nI will now check for duplicate files. This may take a moment.")
    except Exception as e:
        LOGGER.error(f"Could not send initial reply in chat {message.chat.id}: {e}")
        return

    try:
        # Use the imported 'user' client to iterate through the chat history
        async for msg in user.iter_history(message.chat.id):
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

        if messages_to_delete:
            # Use the 'client' (the bot) to send status updates and delete messages
            await client.send_message(message.chat.id, f"Found and deleting {len(messages_to_delete)} duplicate files.")
            
            for i in range(0, len(messages_to_delete), 100):
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=messages_to_delete[i:i + 100]
                )
                await asyncio.sleep(1)
                
            await client.send_message(message.chat.id, "✅ **Cleanup Complete!**")
        else:
            await client.send_message(message.chat.id, "✅ No duplicate files were found.")
            
    except Exception as e:
        LOGGER.error(f"A critical error occurred during the unequify scan in chat {message.chat.id}: {e}")
        await client.send_message(message.chat.id, f"❌ **Error!** An unexpected error occurred: {e}")
