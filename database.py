import sqlite3
import threading


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize_db()
        return cls._instance

    # Add to your Database class
    def _initialize_db(self):
        """Initialize database tables"""
        self.conn = sqlite3.connect("data/database.sqlite3", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                folder_id TEXT NOT NULL UNIQUE
            );
        """
        )
        self.conn.commit()

    def _execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Thread-safe SQL execution."""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor

    # Admin management methods
    def add_admin(self, user_id: int, username: str = None) -> bool:
        try:
            self._execute(
                "INSERT OR IGNORE INTO admins (user_id, username) VALUES (?, ?)",
                (user_id, username),
            )
            return True
        except sqlite3.Error:
            return False

    def remove_admin(self, user_id: int) -> bool:
        cursor = self._execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        return cursor.rowcount > 0

    def is_admin(self, user_id: int) -> bool:
        cursor = self._execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
        return bool(cursor.fetchone())

    def get_all_admins(self) -> list[tuple[int, str]]:
        cursor = self._execute("SELECT user_id, username FROM admins")
        return cursor.fetchall()

    def get_one_admin(self, user_id) -> list[tuple[int, str]]:
        cursor = self._execute(
            "SELECT user_id, username FROM admins WHERE user_id = ?", (user_id,)
        )
        return cursor.fetchone()

    def add_folder(self, name: str, folder_id: str) -> bool:
        try:
            self._execute(
                "INSERT INTO folders (name, folder_id) VALUES (?, ?)", (name, folder_id)
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_folder(self, folder_id: str) -> bool:
        cursor = self._execute("DELETE FROM folders WHERE folder_id = ?", (folder_id,))
        return cursor.rowcount > 0

    def get_all_folders(self) -> list[tuple[int, str]]:
        cursor = self._execute("SELECT name, folder_id FROM folders")
        return cursor.fetchall()

    def get_one_folder(self, folder_id) -> list[tuple[int, str]]:
        cursor = self._execute(
            "SELECT name, folder_id FROM folders WHERE folder_id = ?", (folder_id,)
        )
        return cursor.fetchone()

    def close(self):
        self.conn.close()
