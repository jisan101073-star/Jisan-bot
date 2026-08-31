import os
import random
import logging
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Render-er 24/7 active rakhar jonno Flask Server
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Telegram View Bot is running perfectly! 🚀"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# Environment theke session strings gulo collect korar function
def get_sessions():
    sessions = []
    for i in range(1, 50):
        session = os.getenv(f"SESSION_STRING_{i}")
        if session:
            sessions.append(session)
    return sessions

# View baranor main logic
async def view_post(client, chat_id, message_id):
    try:
        await client.get_messages(chat_id, message_id)
        return True
    except Exception as e:
        logger.error(f"Error viewing message: {e}")
        return False

# Command handlers ebong essential features
def setup_handlers(app, sessions_clients):
    
    # 1. /start - Main Menu & Welcome Message
    @app.on_message(filters.command("start") & filters.private)
    async def handle_start(client, message):
        username = message.from_user.username or "User"
        welcome_text = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "✨ **WELCOME TO VIEW BOT**\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"👋 Hello, @{username}\n\n"
            "💎 Plan      : `FREE`\n"
            "🪙 Credits   : `0`\n"
            "📦 Orders    : `Active`\n"
            "🟢 Status    : `Online`\n\n"
            "📌 **Available Commands:**\n"
            "🔹 `/view [Link] [Amount]` - Post-e view barate\n"
            "🔹 `/stats` - Bot active status dekhte\n\n"
            "Choose a command to start! 👇"
        )
        await message.reply(welcome_text)

    # 2. /stats - Dashboard & Account Status
    @app.on_message(filters.command("stats") & filters.private)
    async def handle_stats(client, message):
        total_accounts = len(sessions_clients)
        stats_text = (
            "╭━━━ 📊 **MY DASHBOARD** ━━━╮\n\n"
            f"👤 User: @{message.from_user.username or 'Admin'}\n"
            f"🆔 ID: `{message.from_user.id}`\n\n"
            f"🤖 Active View Sessions: `{total_accounts}` ta\n"
            "🟢 Bot Status: `Running 24/7`\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await message.reply(stats_text)

    # 3. /view - Create Order / Boost Views
    @app.on_message(filters.command("view") & filters.private)
    async def handle_view_command(client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply(
                "❌ **Bhul command!** Sothik niyome use korun:\n\n"
                "📌 **Format:** `/view [Post_Link] [Amount]`\n"
                "📌 **Example:** `/view https://t.me/channelname/123 10`"
            )
            return
        
        link = args[1]
        if "t.me/" not in link:
            await message.reply("⚠️ Sothik Telegram post link din!")
            return
        
        requested_amount = None
        if len(args) >= 3 and args[2].isdigit():
            requested_amount = int(args[2])

        try:
            parts = link.split("/")
            chat_id = parts[-2]
            message_id = int(parts[-1])
            
            total_available = len(sessions_clients)
            use_count = total_available
            if requested_amount and requested_amount < total_available:
                use_count = requested_amount

            await message.reply(f"🚀 **{use_count}** ti account theke view pathano shuru hocche...")
            
            tasks = []
            for i in range(use_count):
                sess_client = sessions_clients[i]
                await asyncio.sleep(random.uniform(0.1, 0.3))
                tasks.append(view_post(sess_client, chat_id, message_id))
            
            results = await asyncio.gather(*tasks)
            success_count = sum(1 for r in results if r)
            
            await message.reply(f"✅ **Success!** Total `{success_count}` ta view sothikbhave add kora hoiche.")
            
        except Exception as e:
            await message.reply(f"❌ Kono somossa hoisilo: `{str(e)}`")

async def start_userbot(session_string, sessions_clients, is_main=False):
    try:
        api_id = int(os.environ.get("API_ID", 0))
        api_hash = os.environ.get("API_HASH", "")
        
        app = Client(
            name=f"session_{random.randint(1000,9999)}",
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            in_memory=True
        )
        
        await app.start()
        sessions_clients.append(app)
        logger.info("A Pyrogram session started successfully.")
        
        if is_main:
            setup_handlers(app, sessions_clients)
            logger.info("Main control bot handler loaded.")
            
    except Exception as e:
        logger.error(f"Failed to start session: {e}")

async def main():
    Thread(target=run_server, daemon=True).start()
    
    sessions = get_sessions()
    if not sessions:
        logger.warning("Kono SESSION_STRING pawa jayni environment variable-e!")
        return

    sessions_clients = []
    
    tasks = []
    for index, session in enumerate(sessions):
        is_main = (index == 0) # Prothom session-ti diye command control hobe
        tasks.append(start_userbot(session, sessions_clients, is_main))
    
    await asyncio.gather(*tasks)
    logger.info("All view bot sessions are running successfully!")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped gracefully.")
