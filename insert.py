import sqlite3

# Database se connect karo (agar nahi hai toh ye automatically create ho jayega)
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Sample Products List
products = [
    ("Handmade Wooden Box", "Handicraft", 1500.00, "Rajasthan, Uttar Pradesh"),
    ("Clay Pot", "Traditional Pottery", 500.00, "West Bengal, Tamil Nadu"),
    ("Silk Saree", "Textile", 3500.00, "Karnataka, Tamil Nadu"),
    ("Brass Lamp", "Metalwork", 2000.00, "Maharashtra, Gujarat")
]

# Data insert karna (agar pehle se hai toh dobara insert na ho)
cursor.executemany("INSERT INTO products (name, category, price, export_states) VALUES (?, ?, ?, ?)", products)

# Save and Close
conn.commit()
conn.close()

print("✅ Sample Data Inserted Successfully!")
