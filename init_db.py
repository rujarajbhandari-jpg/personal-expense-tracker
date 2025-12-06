from app.db import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Drop tables if you rerun (optional, helpful while developing)
    cur.execute("DROP TABLE IF EXISTS Expenses;")
    cur.execute("DROP TABLE IF EXISTS Categories;")
    cur.execute("DROP TABLE IF EXISTS Users;")

    # Create Users table
    cur.execute("""
    CREATE TABLE Users (
        user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        email         TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at    TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create Categories table
    cur.execute("""
    CREATE TABLE Categories (
        category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE
    );
    """)

    # Create Expenses table
    cur.execute("""
    CREATE TABLE Expenses (
        expense_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        category_id  INTEGER NOT NULL,
        amount       REAL NOT NULL CHECK (amount > 0),
        expense_date TEXT NOT NULL,
        description  TEXT,
        created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (category_id) REFERENCES Categories(category_id)
    );
    """)

    # Insert default categories
    default_categories = [
        ("Food",),
        ("Travel",),
        ("Bills",),
        ("Shopping",),
        ("Entertainment",),
        ("Others",),
    ]

    cur.executemany(
        "INSERT INTO Categories (category_name) VALUES (?);",
        default_categories
    )

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
