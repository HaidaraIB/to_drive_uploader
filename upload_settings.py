from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from DriveServiceSingleton import DriveServiceSingleton
from Config import Config
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
                    callback_data=f"upto {folder["folder_id"]}",
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
        file = (
            await update.message.document.get_file()
            if update.message.document
            else (
                await update.message.video.get_file()
                if update.message.video
                else (
                    await update.message.audio.get_file()
                    if update.message.audio
                    else await update.message.photo[-1].get_file()
                )
            )
        )

        file_path = file.file_path
        file_name = os.path.basename(file_path)

        await update.message.reply_text("جاري التحميل إلى السيرفر ⏳")

        download_path = await file.download_to_drive(f"media/{file_name}")

        await update.message.reply_text("جاري الرفع إلى Google Drive 📤")

        file = DriveServiceSingleton().upload_file(str(download_path), folder_id)
        await update.message.reply_text(
            f"تم الرفع بنجاح ✅: <a href='{file.get('webViewLink')}'>الرابط 🔗</a>"
        )

        os.remove(download_path)
        return ConversationHandler.END
