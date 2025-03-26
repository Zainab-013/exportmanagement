import sqlite3


def get_db_connection():
    """Establish a connection to the SQLite database."""
    try:
        conn = sqlite3.connect('database.db')  # Database file (stores data)
        conn.row_factory = sqlite3.Row  # Allows column access by name
        return conn
    except sqlite3.Error as e:
        print("Database connection error:", e)
        return None
    
def create_tables():
     
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        # ✅ Fix Users Table (Added role column and fixed password field)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database and tables created successfully!")

if __name__ == '__main__':
    create_tables()
