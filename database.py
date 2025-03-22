import sqlite3

def get_db_connection():
    try:
        conn = sqlite3.connect('products.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print("Database connection error:", e)
        return None

def create_tables():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        # ✅ Users Table (Login System ke liye)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT
                NOT NULL
            )
        ''')

        # ✅ Products Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price INTEGER NOT NULL,
                export_states TEXT NOT NULL
            )
        ''')

        # ✅ Orders Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # ✅ Order Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database aur saari tables create ho gayi!")

if __name__ == '__main__':
    create_tables()
