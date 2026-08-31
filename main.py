import os
import random
import logging
import asyncio
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Render-er 24/7 active rakhar jonno Flask Server
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Telegram View Bot (Telethon) is running perfectly! 🚀"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

def get_sessions():
    sessions = []
    for i in range(1, 50):
        session = os.getenv(f"SESSION_STRING_{i}")
        if session:
            sessions.append(session)
    return sessions

async def main():
    # Background-e Flask server run korano
    Thread(target=run_server, daemon=True).start()
    
    sessions = get_sessions()
    if not sessions:
        logger.warning("Kono SESSION_STRING pawa jayni environment variable-e!")
        return

    api_id = int(os.environ.get("API_ID", 0))
    api_hash = os.environ.get("API_HASH", "")
    
    clients = []
    
    # StringSession use kore main client start kora
    print("Starting main session...")
    main_client = TelegramClient(StringSession(sessions[0]), api_id, api_hash)
    await main_client.start()
    clients.append(main_client)
    
    # 1. /start Handler
    @main_client.on(events.NewMessage(pattern='/start', outgoing=False))
    async def handle_start(event):
        if not event.is_private:
            return
        sender = await event.get_sender()
        username = sender.username or "User"
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
        await event.respond(welcome_text)

    # 2. /stats Handler
    @main_client.on(events.NewMessage(pattern='/stats', outgoing=False))
    async def handle_stats(event):
        if not event.is_private:
            return
        total_accounts = len(clients)
        stats_text = (
            "╭━━━ 📊 **MY DASHBOARD** ━━━╮\n\n"
            f"🆔 ID: `{event.sender_id}`\n\n"
            f"🤖 Active View Sessions: `{total_accounts}` ta\n"
            "🟢 Bot Status: `Running 24/7`\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await event.respond(stats_text)

    # 3. /view Handler
    @main_client.on(events.NewMessage(pattern='/view', outgoing=False))
    async def handle_view(event):
        if not event.is_private:
            return
        
        args = event.text.split()
        if len(args) < 2:
            await event.respond(
                "❌ **Bhul command!** Sothik niyome use korun:\n\n"
                "📌 **Format:** `/view [Post_Link] [Amount]`\n"
                "📌 **Example:** `/view https://t.me/channelname/123 10`"
            )
            return
        
        link = args[1]
        if "t.me/" not in link:
            await event.respond("⚠️ Sothik Telegram post link din!")
            return
        
        requested_amount = None
        if len(args) >= 3 and args[2].isdigit():
            requested_amount = int(args[2])

        try:
            if "/c/" in link:
                parts = link.split("/")
                chat_id = int("-100" + parts[-2])
                message_id = int(parts[-1])
            else:
                parts = link.split("/")
                chat_id = parts[-2]
                message_id = int(parts[-1])
            
            total_available = len(clients)
            use_count = total_available
            if requested_amount and requested_amount < total_available:
                use_count = requested_amount

            await event.respond(f"🚀 **{use_count}** ti account theke view pathano shuru hocche...")
            
            success_count = 0
            for i in range(use_count):
                client = clients[i]
                try:
                    await client.get_messages(chat_id, ids=message_id)
                    success_count += 1
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.error(f"View error: {e}")
            
            await event.respond(f"✅ **Success!** Total `{success_count}` ta view sothikbhave add kora hoiche.")
            
        except Exception as e:
            await event.respond(f"❌ Kono somossa hoisilo: `{str(e)}`")

    # Baki session gulo connect korbo
    for idx, session in enumerate(sessions[1:], start=2):
        try:
            print(f"Starting extra session {idx}...")
            extra_client = TelegramClient(StringSession(session), api_id, api_hash)
            await extra_client.start()
            clients.append(extra_client)
        except Exception as e:
            logger.error(f"Failed to start session {idx}: {e}")

    logger.info("All Telethon view bot sessions are running successfully!")
    await main_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped gracefully.")
