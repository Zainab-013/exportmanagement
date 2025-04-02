import sqlite3

def get_db_connection():
    """Establish a connection to the SQLite database."""
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print("Database connection error:", e)
        return None

def create_tables():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        # ✅ Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        # ✅ Products Table. Added vendor column.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                export_states TEXT NOT NULL,
                vendor TEXT NOT NULL
            )
        ''')

        # ✅ Orders Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                vendor TEXT NOT NULL,
                total_amount REAL NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
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

        # Insert sample data after tables are created
        insert_sample_data(conn, cursor)
        conn.commit()
        conn.close()
        print("✅ Database aur saari tables create ho gayi!")

def insert_sample_data(conn, cursor):
    """Insert sample product data if the products table is empty."""
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]

    if count == 0:
        products = [
            ("Handmade Wooden Box", "Handicraft", 1500, "Rajasthan, Uttar Pradesh", "Vendor A"),
            ("Clay Pot", "Traditional Pottery", 500, "West Bengal, Tamil Nadu", "Vendor B"),
            ("Silk Saree", "Textile", 3500, "Karnataka, Tamil Nadu", "Vendor C"),
            ("Brass Lamp", "Metalwork", 2000, "Maharashtra, Gujarat", "Vendor D")
        ]

        cursor.executemany('''
            INSERT INTO products (name, category, price, export_states, vendor)
            VALUES (?, ?, ?, ?, ?)
        ''', products)
        print("✅ Sample products insert ho gaye!")
        conn.commit()

if __name__ == '__main__':
    create_tables()