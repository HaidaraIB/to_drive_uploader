from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from Config import Config

# States for ConversationHandler
ADDING_FOLDER, REMOVING_FOLDER = range(2)


async def add_folder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        await update.message.reply_text(
            "أرسل اسم المجلد والGoogle Drive File ID الخاص به 📝\n"
            "مثال:\n"
            "<code>MyFolder\n"
            "1AbCdEfGhIjKlMnOpQrStUvWxYz</code>\n\n"
            "أو اضغط /cancel للإلغاء.",
        )
        return ADDING_FOLDER


async def add_folder_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        name, folder_id = update.message.text.split("\n")
        Config.add_folder(name, folder_id)
        await update.message.reply_text(f"تمت إضافة المجلد ✅: <code>{name}</code>")
        return ConversationHandler.END


async def remove_folder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        folders = Config.get_all_folders()
        if not folders:
            await update.message.reply_text("ليس لديك مجلدات لإزالتها ⚠️")
            return ConversationHandler.END

        keyboard = [
            [
                InlineKeyboardButton(
                    folder["name"],
                    callback_data=f"rmfolder_{folder["folder_id"]}",
                )
            ]
            for folder in folders
        ]

        await update.message.reply_text(
            "اختر المجلد لإزالته 🗑:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return REMOVING_FOLDER


async def remove_folder_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        folder_id = update.callback_query.data.split("_")[-1]
        folder = Config.get_one_folder(folder_id)
        Config.remove_folder(folder_id)
        await update.callback_query.edit_message_text(
            f"تمت إزالة المجلد ✅: <code>{folder['name']}</code>"
        )
        return ConversationHandler.END
