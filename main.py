#from bot import Bot

#app = Bot()
#app.run()
from bot import Bot, user
from pyrogram import idle

# Create an instance of the bot
app = Bot()

async def main():
    """Starts both the bot and the user clients concurrently."""
    print("Starting clients...")
    # Start both clients together
    await app.start()
    await user.start()
    print("Clients have started successfully.")
    
    # Wait for the program to be stopped
    await idle()
    
    # Stop both clients gracefully
    print("Stopping clients...")
    await app.stop()
    await user.stop()

if __name__ == "__main__":
    app.run(main())

