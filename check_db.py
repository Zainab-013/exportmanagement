import sqlite3

# Database connect karo
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Products Table se saara data fetch karo
cursor.execute("SELECT * FROM products")
data = cursor.fetchall()

# Data print karo
for row in data:
    print(row)

conn.close()
