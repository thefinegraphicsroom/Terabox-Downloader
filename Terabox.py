import asyncio
from concurrent.futures import ThreadPoolExecutor
from tkinter import Message
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from pyrogram.enums import ChatMemberStatus
from typing import Dict, Any, Tuple
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import UTC, datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
ADMIN_IDS = [1949883614]  
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL")

# URLs and API Configuration
WEBAPP_URL = os.getenv("WEBAPP_URL")
# Media URLs
TERABOX_IMAGE = os.getenv("TERABOX_IMAGE")
NONVEG_IMAGE = os.getenv("NONVEG_IMAGE")
WELCOME_VIDEO = os.getenv("WELCOME_VIDEO")

# Configure worker pools
MAX_WORKERS = 1000

class CombinedBot:
    def __init__(self):
        self.app = Client(
            "Terabox_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=1000
        )
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    async def get_user_stats(self):
        """Get user activity statistics"""
        now = datetime.now(UTC)
        
        one_day_ago = now - timedelta(days=1)
        one_week_ago = now - timedelta(weeks=1)
        one_month_ago = now - timedelta(days=30)
        one_year_ago = now - timedelta(days=365)
        
        total_users = await self.db.users.count_documents({})
        
        day_active = await self.db.users.count_documents({"last_active": {"$gte": one_day_ago}})
        week_active = await self.db.users.count_documents({"last_active": {"$gte": one_week_ago}})
        month_active = await self.db.users.count_documents({"last_active": {"$gte": one_month_ago}})
        year_active = await self.db.users.count_documents({"last_active": {"$gte": one_year_ago}})
        
        return {
            "day": day_active,
            "week": week_active,
            "month": month_active,
            "year": year_active,
            "total": total_users
        }

    async def send_log(self, text: str):
        """Send logs to the private channel"""
        try:
            await self.app.send_message(LOG_CHANNEL, text)
        except Exception as e:
            logger.error(f"Failed to send log: {e}")
        
    async def start(self):
        """Initialize the bot and MongoDB connection"""
        await self.app.start()
        self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.mongo_client.Terabox
        logger.info("Bot started successfully")

    async def stop(self):
        """Cleanup resources"""
        await self.app.stop()
        self.executor.shutdown()
        self.mongo_client.close()
        logger.info("Bot stopped successfully")

    async def store_user(self, user):
        """Store user data with last active timestamp"""
        try:
            user_data = {
                "user_id": user.id,
                "username": user.username or "No username",
                "last_active": datetime.now(UTC)
            }
            
            await self.db.users.update_one(
                {"user_id": user.id},
                {"$set": user_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error storing user data: {e}")

    async def check_member(self, user_id: int) -> bool:
        """Check if user is a member of the required channel"""
        try:
            member = await self.app.get_chat_member(CHANNEL_USERNAME, user_id)
            return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except errors.UserNotParticipant:
            return False
        except Exception as e:
            logger.debug(f"Unexpected error in check_member: {str(e)}")
            return False

    def get_force_sub_buttons(self) -> InlineKeyboardMarkup:
        """Generate force subscribe buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
            ],
            [
                InlineKeyboardButton("🔍 Check Membership", callback_data="check_membership")
            ]
        ])

    async def send_force_sub_message(self, chat_id: int):
        """Send force subscribe message"""
        text = (
            "🔒 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗠𝗲𝗺𝗯𝗲𝗿𝘀𝗵𝗶𝗽 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱\n\n"
            f"- ᴊᴏɪɴ {CHANNEL_USERNAME} ᴛᴏ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ\n"
            "- ᴄʟɪᴄᴋ \"✅ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ\" ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ\n"
            "- ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴄʟɪᴄᴋ ᴏɴ \"🔍 ᴄʜᴇᴄᴋ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\" ʙᴜᴛᴛᴏɴ"
        )
        await self.app.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=self.get_force_sub_buttons()
        )

    async def handle_start_command(self, client, message):
        """Handle the /start command"""
        log_text = (
            "🤖 Bot Start\n"
            f"User: {message.from_user.mention} [`{message.from_user.id}`]\n"
            f"Username: @{message.from_user.username or 'None'}"
        )
        await self.send_log(log_text)

        await self.store_user(message.from_user)
        
        user_mention = message.from_user.mention
        welcome_text = (
            f"**👋 Welcome {user_mention}!**\n\n"
            "**🌟 I'm your Terabox Download and Non-Veg Assistant! Here's what I can do:**\n\n"
            "**📥 Send me any Terabox link to:**\n"
            "**📥 Send me /nonveg command and see magic:**\n"
            "**• Watch files online**\n"
            "**• Access file details**\n\n"
            "**💫 Just send me a link to get started!**"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"),
                InlineKeyboardButton("👨‍💻 Owner", url="https://t.me/Hmm_Smokie")
            ]
        ])

        try:
            await client.send_video(
                chat_id=message.chat.id,
                video=WELCOME_VIDEO,
                caption=welcome_text,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            await message.reply_text(
                text=welcome_text,
                reply_markup=keyboard
            )

    def create_reply_markup(self, terabox_link: str) -> InlineKeyboardMarkup:
        """Create inline keyboard markup with WebApp button"""
        watch_url = f"{WEBAPP_URL}{terabox_link}"
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎬 Watch in Mini App",
                    web_app=WebAppInfo(url=watch_url)
                )
            ]
        ])

    async def handle_terabox_link(self, client, message):
        """Handle incoming Terabox links"""
        log_text = (
            "📥 New Link Received\n"
            f"User: {message.from_user.mention} [`{message.from_user.id}`]\n"
            f"Link: {message.text}"
        )
        await self.send_log(log_text)

        if not await self.check_member(message.from_user.id):
            await self.send_force_sub_message(message.chat.id)
            return

        terabox_link = message.text.strip()
        try:
            reply_markup = self.create_reply_markup(terabox_link)
            await message.reply_photo(
                photo=TERABOX_IMAGE,
                caption="Boom! Your File Link is Good to Go!\n\nＰＯＷＥＲＥＤ ＢＹ ＰＯＲＮＨＵＢ Ｘ ＴＥＲＡＢＯＸ",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error processing link: {str(e)}", exc_info=True)
            await message.reply_text(
                "An error occurred while processing your request. Please try again later."
            )

    async def handle_callback_query(self, client, callback_query):
        """Handle callback queries for membership check"""
        try:
            is_member = await self.check_member(callback_query.from_user.id)
            
            if is_member:
                log_text = (
                    "✅ Successful Membership Check\n"
                    f"User: {callback_query.from_user.mention} [`{callback_query.from_user.id}`]"
                )
                await self.send_log(log_text)
                
                await callback_query.message.edit_text(
                    "✅ Now You Can Send Me Terabox Links.",
                )
            else:
                await callback_query.answer(
                    "❌ You haven't joined the channel yet. Please join first!",
                    show_alert=True
                )
        except Exception as e:
            logger.debug(f"Error in callback query: {e}")
            await callback_query.answer(
                "Please try again.",
                show_alert=True
            )

    async def handle_nonveg_reel(self, client, message):
        """Handle the nonveg_reel command"""
        log_text = (
            "🎬 NonVeg Reel Request\n"
            f"User: {message.from_user.mention} [`{message.from_user.id}`]"
        )
        await self.send_log(log_text)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Non Veg Reels",
                    web_app=WebAppInfo(url="https://fikfap.com/")
                )
            ]
        ])

        await client.send_photo(
            chat_id=message.chat.id,
            photo=NONVEG_IMAGE,
            caption="💥 Unlock your Mini App now! Just tap the button below!\n\nＰＯＷＥＲＥＤ ＢＹ ＰＯＲＮＨＵＢ Ｘ ＭＩＮＩ ＡＰＰ",
            reply_markup=keyboard
        )

    async def broadcast_message(self, message: Message, user_id: int) -> Tuple[bool, str]:
        try:
            caption = message.caption
            reply_markup = message.reply_markup
            
            if message.text:
                await self.app.send_message(
                    chat_id=user_id,
                    text=message.text,
                    entities=message.entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.photo:
                await self.app.send_photo(
                    chat_id=user_id,
                    photo=message.photo.file_id,
                    caption=caption,
                    caption_entities=message.caption_entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.video:
                await self.app.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=caption,
                    caption_entities=message.caption_entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.audio:
                await self.app.send_audio(
                    chat_id=user_id,
                    audio=message.audio.file_id,
                    caption=caption,
                    caption_entities=message.caption_entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.document:
                await self.app.send_document(
                    chat_id=user_id,
                    document=message.document.file_id,
                    caption=caption,
                    caption_entities=message.caption_entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.animation:
                await self.app.send_animation(
                    chat_id=user_id,
                    animation=message.animation.file_id,
                    caption=caption,
                    caption_entities=message.caption_entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.sticker:
                await self.app.send_sticker(
                    chat_id=user_id,
                    sticker=message.sticker.file_id,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.voice:
                await self.app.send_voice(
                    chat_id=user_id,
                    voice=message.voice.file_id,
                    caption=caption,
                    caption_entities=message.caption_entities,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            elif message.video_note:
                await self.app.send_video_note(
                    chat_id=user_id,
                    video_note=message.video_note.file_id,
                    reply_markup=reply_markup,
                    disable_notification=True
                )
            return True, ""
        except errors.UserIsBlocked:
            # Silently handle blocked users
            return False, "user_blocked"
        except Exception as e:
            logger.debug(f"Broadcast failed for user {user_id}: {str(e)}")
            return False, str(e)

    async def broadcast_to_users(self, message: Message, admin_msg: Message = None):
        all_users = await self.db.users.find().to_list(length=None)
        success_count = 0
        failed_count = 0
        blocked_count = 0
        
        for user in all_users:
            success, error = await self.broadcast_message(message, user["user_id"])
            if success:
                success_count += 1
            else:
                if error == "user_blocked":
                    blocked_count += 1
                else:
                    failed_count += 1
            
            if admin_msg and (success_count + failed_count + blocked_count) % 5 == 0:
                await admin_msg.edit_text(
                    f"Broadcast Status:\n"
                    f"Total Users: {len(all_users)}\n"
                    f"Completed: {success_count + failed_count + blocked_count}\n"
                    f"Success: {success_count}\n"
                    f"Blocked: {blocked_count}\n"
                    f"Failed: {failed_count}"
                )
            
            await asyncio.sleep(0.05)
        
        return success_count, failed_count + blocked_count

async def main():
    """Main entry point"""
    bot = CombinedBot()
    
    try:
        @bot.app.on_message(filters.command("start"))
        async def start_command(client, message):
            await bot.handle_start_command(client, message)

        @bot.app.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
        async def stats_command(client, message):
            try:
                stats = await bot.get_user_stats()
                stats_text = (
                    "**📊 Terabox Bot Status ⇾ Report ✅**\n"
                    "━━━━━━━━━━━━━━━━\n"
                    f"**1 Day: {stats['day']} users were active**\n"
                    f"**1 Week: {stats['week']} users were active**\n"
                    f"**1 Month: {stats['month']} users were active**\n"
                    f"**1 Year: {stats['year']} users were active**\n"
                    "━━━━━━━━━━━━━━━━\n"
                    f"**Total TeraBox Users: {stats['total']}**"
                )
                await message.reply_text(stats_text)
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                await message.reply_text("Error retrieving statistics.")
            
        @bot.app.on_message(filters.regex(r"^(?:http|https)://"))
        async def handle_message(client, message):
            await bot.handle_terabox_link(client, message)

        @bot.app.on_message(filters.command("nonveg"))
        async def nonveg_command(client, message):
            await bot.handle_nonveg_reel(client, message)

        @bot.app.on_callback_query()
        async def handle_callback(client, callback_query):
            await bot.handle_callback_query(client, callback_query)

        @bot.app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
        async def broadcast_handler(client, message):
            if not message.reply_to_message:
                await message.reply_text("Please reply to a message to broadcast it.")
                return
            
            status_msg = await message.reply_text("Starting broadcast...")
            success, failed = await bot.broadcast_to_users(
                message.reply_to_message, 
                status_msg
            )
            
            await status_msg.edit_text(
                f"Broadcast Completed!\n"
                f"Success: {success}\n"
                f"Failed: {failed}"
            )
        
        await bot.start()
        await asyncio.Event().wait()

        @bot.app.on_callback_query()
        async def callback_query(client, callback_query):
            await bot.handle_callback_query(client, callback_query)

        await bot.start()
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
    finally:
        await bot.stop()

if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(main())
