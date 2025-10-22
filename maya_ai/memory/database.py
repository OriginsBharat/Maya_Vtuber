import sqlite3
from pathlib import Path

class MemoryDatabase:
    """
    Handles the SQLite database for storing memories.
    This includes user profiles and conversation history.
    """
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """
        Creates the necessary tables if they don't already exist.
        """
        cursor = self.conn.cursor()
        # User profile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        self.conn.commit()

    def get_or_create_user(self, username: str) -> int:
        """
        Gets a user by username, creating them if they don't exist.
        Returns the user's ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            return user[0]
        else:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            self.conn.commit()
            return cursor.lastrowid

    def log_message(self, user_id: int, role: str, content: str):
        """
        Logs a message to the conversation history.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        self.conn.commit()

    def get_history(self, user_id: int, limit: int = 20) -> list:
        """
        Retrieves the recent conversation history for a user.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT role, content FROM (
                SELECT role, content, id FROM history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) sub
            ORDER BY sub.id ASC
            """,
            (user_id, limit)
        )
        history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        return history

    def close(self):
        """Closes the database connection."""
        self.conn.close()