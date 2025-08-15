from dotenv import load_dotenv
import os
from database import Database

load_dotenv()

db = Database()

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
    REFRESH_TOKEN_FILE = os.getenv("REFRESH_TOKEN_FILE")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    @staticmethod
    def add_folder(name: str, folder_id: str) -> bool:
        return db.add_folder(name, folder_id)

    @staticmethod
    def remove_folder(folder_id: str) -> bool:
        return db.remove_folder(folder_id)

    @staticmethod
    def get_all_folders():
        return db.get_all_folders()

    @staticmethod
    def get_one_folder(folder_id):
        return db.get_one_folder(folder_id)

    @staticmethod
    def add_admin(user_id, identifier):
        return db.add_admin(user_id, identifier)

    @staticmethod
    def remove_admin(user_id):
        return db.remove_admin(user_id)

    @staticmethod
    def get_all_admins():
        return db.get_all_admins()

    @staticmethod
    def get_one_admin(user_id):
        return db.get_one_admin(user_id)

    @staticmethod
    def is_admin(user_id: int) -> bool:
        return db.is_admin(user_id)
