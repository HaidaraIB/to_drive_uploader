from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from DriveServiceSingleton import DriveServiceSingleton
from Config import Config
from TeleClientSingleton import TeleClientSingleton
import os

DRIVE_FOLDER, FILE = range(2)


async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        folders = Config.get_all_folders()
        if not folders:
            await update.message.reply_text("ليس لديك مجلدات بعد ⚠️")
            return ConversationHandler.END
        keyboard = [
            [
                InlineKeyboardButton(
                    folder["name"],
                    callback_data=f"upto {folder['folder_id']}",
                )
            ]
            for folder in folders
        ]
        await update.message.reply_text(
            "اختر المجلد الذي تريد الرفع إليه:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return DRIVE_FOLDER


async def folder_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        folder_id_to_upload_to = update.callback_query.data.split()[-1]
        context.user_data["folder_id_to_upload_to"] = folder_id_to_upload_to
        await update.callback_query.edit_message_text("أرسل الملف الآن 📤")
        return FILE


async def upload_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        folder_id = context.user_data["folder_id_to_upload_to"]
        message = update.message

        # Determine file name
        if message.document:
            file_name = message.document.file_name
        elif message.video:
            file_name = message.video.file_name or f"video_{message.video.file_id}.mp4"
        elif message.audio:
            file_name = message.audio.file_name or f"audio_{message.audio.file_id}.mp3"
        elif message.photo:
            file_name = f"photo_{message.photo[-1].file_id}.jpg"
        else:
            await message.reply_text("نوع الملف غير مدعوم ⚠️")
            return ConversationHandler.END

        download_path = f"media/{file_name}"

        await message.reply_text("جاري التحميل إلى السيرفر ⏳")

        # Check file size to determine download method
        file_size = 0
        if message.document:
            file_size = message.document.file_size
        elif message.video:
            file_size = message.video.file_size
        elif message.audio:
            file_size = message.audio.file_size
        elif message.photo:
            file_size = message.photo[-1].file_size

        if file_size and file_size > 20 * 1024 * 1024:  # 20MB
            # Use Telethon for large files
            try:
                client = TeleClientSingleton()
                fwdd_msg = await context.bot.forward_message(
                    chat_id=Config.MEDIA_CHANNEL_ID,
                    from_chat_id=update.effective_chat.id,
                    message_id=update.effective_message.id,
                )
                # Get the message using Telethon
                telethon_message = await client.get_messages(
                    Config.MEDIA_CHANNEL_ID, ids=fwdd_msg.id
                )

                # Download using Telethon
                await client.download_media(telethon_message, file=download_path)

                if not download_path or not os.path.exists(download_path):
                    await message.reply_text("فشل تحميل الملف ⚠️")
                    return ConversationHandler.END
            except Exception as e:
                await message.reply_text(f"حدث خطأ أثناء تحميل الملف الكبير: {str(e)}")
                return ConversationHandler.END
        else:
            # Use regular bot API for small files
            file = (
                await message.document.get_file()
                if message.document
                else (
                    await message.video.get_file()
                    if message.video
                    else (
                        await message.audio.get_file()
                        if message.audio
                        else await message.photo[-1].get_file()
                    )
                )
            )
            await file.download_to_drive(download_path)

        await message.reply_text("جاري الرفع إلى Google Drive 📤")

        try:
            file = DriveServiceSingleton().upload_file(download_path, folder_id)
            await message.reply_text(
                f"تم الرفع بنجاح ✅: <a href='{file.get('webViewLink')}'>الرابط 🔗</a>"
            )
        except Exception as e:
            await message.reply_text(f"حدث خطأ أثناء الرفع إلى Google Drive: {str(e)}")

        # Clean up
        if os.path.exists(download_path):
            os.remove(download_path)

        return ConversationHandler.END
