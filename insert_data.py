from database import get_db_connection

def insert_sample_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        products = [
            ("Handmade Wooden Box", "Handicraft", 1500, "Rajasthan, Uttar Pradesh"),
            ("Clay Pot", "Traditional Pottery", 500, "West Bengal, Tamil Nadu"),
            ("Silk Saree", "Textile", 3500, "Karnataka, Tamil Nadu"),
            ("Brass Lamp", "Metalwork", 2000, "Maharashtra, Gujarat")
        ]

        cursor.executemany('''
            INSERT INTO products (name, category, price, export_states)
            VALUES (?, ?, ?, ?)
        ''', products)

        conn.commit()
        conn.close()
        print("✅ Sample products insert ho gaye!")

if __name__ == '__main__':
    insert_sample_data()
