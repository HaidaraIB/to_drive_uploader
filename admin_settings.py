from telegram import (
    Chat,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    KeyboardButtonRequestUsers,
)
from telegram.ext import ContextTypes, ConversationHandler
from Config import Config

ADDING_ADMIN, REMOVING_ADMIN = range(2)


async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        await update.message.reply_text(
            "اختر المستخدم 👤",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(
                    text="اختر المستخدم 👤",
                    request_users=KeyboardButtonRequestUsers(
                        request_id=1,
                        user_is_bot=False,
                    ),
                ),
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return ADDING_ADMIN


async def add_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        user = update.message.users_shared.users[0]
        selected_user_id = user.user_id
        user_chat = await context.bot.get_chat(selected_user_id)

        if Config.is_admin(selected_user_id):
            await update.message.reply_text(
                "هذا المستخدم آدمن بالفعل ⚠️",
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            Config.add_admin(
                selected_user_id,
                user_chat.username or user_chat.full_name,
            )
            await update.message.reply_text(
                f"تمت إضافة الآدمن ✅: {user_chat.full_name}",
                reply_markup=ReplyKeyboardRemove(),
            )

        return ConversationHandler.END


async def remove_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):

        admins = Config.get_all_admins()
        keyboard = [
            [
                InlineKeyboardButton(
                    admin["username"],
                    callback_data=f"rmadmin_{admin['user_id']}",
                )
            ]
            for admin in admins
        ]
        await update.message.reply_text(
            "اختر الآدمن لإزالته 🗑:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return REMOVING_ADMIN


async def remove_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        user_id = int(update.callback_query.data.split("_")[-1])
        if user_id == Config.OWNER_ID:
            await update.callback_query.answer(
                "لا يمكنك إزالة مالك البوت من قائمة المشرفين ⚠️",
                show_alert=True,
            )
            return
        admin = Config.get_one_admin(user_id)
        Config.remove_admin(user_id)
        await update.callback_query.edit_message_text(
            f"تمت إزالة الآدمن ✅: {admin['username']}"
        )
        return ConversationHandler.END
