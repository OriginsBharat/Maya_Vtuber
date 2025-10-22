import unittest
from pathlib import Path
import sqlite3
from maya_ai.memory.database import MemoryDatabase

class TestMemoryDatabase(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database for each test."""
        self.db_path = Path(":memory:") # Use an in-memory SQLite database for tests
        self.memory_db = MemoryDatabase(db_path=self.db_path)
        # We need to manage the connection directly for in-memory DB
        self.conn = self.memory_db.conn

    def tearDown(self):
        """Close the connection after each test."""
        self.conn.close()

    def test_01_create_tables(self):
        """Test if tables are created successfully."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        self.assertIsNotNone(cursor.fetchone(), "'users' table should exist.")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
        self.assertIsNotNone(cursor.fetchone(), "'history' table should exist.")

    def test_02_get_or_create_user(self):
        """Test creating and retrieving a user."""
        # Create a new user
        user_id_1 = self.memory_db.get_or_create_user("testuser")
        self.assertIsInstance(user_id_1, int)

        # Retrieve the same user
        user_id_2 = self.memory_db.get_or_create_user("testuser")
        self.assertEqual(user_id_1, user_id_2, "Should return the same user ID.")

        # Create another user
        user_id_3 = self.memory_db.get_or_create_user("anotheruser")
        self.assertNotEqual(user_id_1, user_id_3, "Different users should have different IDs.")

    def test_03_log_and_get_history(self):
        """Test logging and retrieving conversation history."""
        user_id = self.memory_db.get_or_create_user("historyuser")

        # Log some messages
        self.memory_db.log_message(user_id, "user", "Hello, Maya!")
        self.memory_db.log_message(user_id, "assistant", "Hello, creator!")
        self.memory_db.log_message(user_id, "user", "How are you?")

        # Retrieve history
        history = self.memory_db.get_history(user_id)
        self.assertEqual(len(history), 3)

        # Check content and order
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[0]['content'], 'Hello, Maya!')
        self.assertEqual(history[2]['role'], 'user')
        self.assertEqual(history[2]['content'], 'How are you?')

    def test_04_history_limit(self):
        """Test if the history limit is respected."""
        user_id = self.memory_db.get_or_create_user("limituser")
        for i in range(10):
            self.memory_db.log_message(user_id, "user", f"Message {i}")

        history = self.memory_db.get_history(user_id, limit=5)
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0]['content'], "Message 5") # Should get the latest 5

if __name__ == "__main__":
    unittest.main()