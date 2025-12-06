import sqlite3
import os

# Path to the SQLite database file
DB_NAME = "expense_tracker.db"

def get_db_path():
    """Return the absolute path to the database file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DB_NAME)

def get_connection():
    """Create a new DB connection and return it."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # so we can access columns by name
    return conn
