from telegram import (
    Chat,
    Update,
    MenuButtonCommands,
    BotCommand,
    BotCommandScopeChat,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Defaults,
    PicklePersistence,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode
from admin_settings import (
    ADDING_ADMIN,
    REMOVING_ADMIN,
    add_admin_start,
    add_admin_process,
    remove_admin_start,
    remove_admin_process,
)
from folder_settings import (
    ADDING_FOLDER,
    REMOVING_FOLDER,
    add_folder_start,
    add_folder_process,
    remove_folder_start,
    remove_folder_process,
)
from upload_settings import (
    DRIVE_FOLDER,
    FILE,
    upload_start,
    folder_choice,
    upload_process,
)
from Config import Config
from database import Database
from warnings import filterwarnings


from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*the `days` parameter.*", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*invalid escape sequence.*", category=SyntaxWarning
)


import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def set_bot_commands_advanced(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    admin_commands = [
        ("start", "Start the bot"),
        ("cancel", "Cancel a process"),
        ("addfolder", "Add new Google Drive folder"),
        ("removefolder", "Remove a folder"),
        ("addadmin", "Add new admin"),
        ("removeadmin", "Remove an admin"),
        ("upload", "Start upload process"),
    ]

    await context.bot.set_my_commands(
        [BotCommand(cmd, desc) for cmd, desc in admin_commands],
        scope=BotCommandScopeChat(user_id),
    )

    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        await set_bot_commands_advanced(context, update.effective_user.id)
        await update.message.reply_text(
            "أهلاً بك",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.type == Chat.PRIVATE and Config.is_admin(
        update.effective_user.id
    ):
        await update.message.reply_text("تم الإلغاء ❌")
        return ConversationHandler.END


async def post_init(context: ContextTypes.DEFAULT_TYPE):
    # Add the first admin from environment if needed
    if Config.OWNER_ID:
        db.add_admin(Config.OWNER_ID, "Owner")


if __name__ == "__main__":
    # Initialize database
    db = Database()

    defaults = Defaults(parse_mode=ParseMode.HTML)
    my_persistence = PicklePersistence(filepath="data/persistence", single_file=False)
    app = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .persistence(persistence=my_persistence)
        .defaults(defaults)
        .concurrent_updates(True)
        .build()
    )

    start_cmd = CommandHandler("start", start)
    cancel_cmd = CommandHandler(
        ["cancel", "stop", "exit"],
        cancel,
    )

    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "addadmin",
                    add_admin_start,
                )
            ],
            states={
                ADDING_ADMIN: [
                    MessageHandler(
                        filters.StatusUpdate.USERS_SHARED,
                        add_admin_process,
                    )
                ]
            },
            fallbacks=[start_cmd, cancel_cmd],
            allow_reentry=True,
        )
    )

    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "removeadmin",
                    remove_admin_start,
                )
            ],
            states={
                REMOVING_ADMIN: [
                    CallbackQueryHandler(
                        remove_admin_process,
                        r"^rmadmin_",
                    )
                ]
            },
            fallbacks=[start_cmd, cancel_cmd],
            allow_reentry=True,
        )
    )

    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "addfolder",
                    add_folder_start,
                )
            ],
            states={
                ADDING_FOLDER: [
                    MessageHandler(
                        filters.Regex(r"^.+\n.+$"),
                        add_folder_process,
                    )
                ]
            },
            fallbacks=[start_cmd, cancel_cmd],
            allow_reentry=True,
        )
    )
    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "removefolder",
                    remove_folder_start,
                )
            ],
            states={
                REMOVING_FOLDER: [
                    CallbackQueryHandler(
                        remove_folder_process,
                        r"^rmfolder_",
                    )
                ]
            },
            fallbacks=[start_cmd, cancel_cmd],
            allow_reentry=True,
        )
    )
    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "upload",
                    upload_start,
                )
            ],
            states={
                DRIVE_FOLDER: [
                    CallbackQueryHandler(
                        folder_choice,
                        r"^upto ",
                    )
                ],
                FILE: [
                    MessageHandler(
                        (
                            filters.Document.ALL
                            | filters.VIDEO
                            | filters.AUDIO
                            | filters.PHOTO
                        ),
                        upload_process,
                    )
                ],
            },
            fallbacks=[start_cmd, cancel_cmd],
            allow_reentry=True,
        )
    )
    app.add_handler(start_cmd)
    app.add_handler(cancel_cmd)

    app.run_polling(close_loop=False)
    db.close()
