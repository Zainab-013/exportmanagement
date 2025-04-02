import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
import bcrypt
from fpdf import FPDF  # For PDF generation
from database import get_db_connection


app = Flask(__name__)
app.secret_key = 'your_secret_key'

DOCUMENTS_FOLDER = "export_documents/"
os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)  # Ensure the folder exists

# ✅ Jinja Filter for Checking File Existence
@app.template_filter('file_exists')
def file_exists_filter(filename):
    return os.path.exists(os.path.join(DOCUMENTS_FOLDER, filename))

app.jinja_env.filters['file_exists'] = file_exists_filter
# 🏠 **Home Page**
@app.route('/')
def home():
    return render_template('home.html')

# ✅ **User Registration**
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Capture role

        # ✅ Hash password correctly
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # ✅ Insert hashed password and role into database
            cursor.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                           (name, email, hashed_password, role))
            conn.commit()
            conn.close()
            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("⚠ Email already exists! Try a different one.", "danger")

    return render_template('register.html')


# ✅ **User Login with Role-Based Redirection**
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):  # ✅ Fix comparison
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']  # ✅ Store role in session

            flash("✅ Login successful!", "success")

            # ✅ Redirect based on user role
            if user['role'] == "Export_Manager":
                return redirect(url_for('Export_Manager_dashboard'))
            elif user['role'] == "vendor":
                return redirect(url_for('vendor_dashboard'))
            elif user['role'] == "logistics":
                return redirect(url_for('logistics_dashboard'))
            else:
                flash("⚠ Unauthorized role!", "danger")
                return redirect(url_for('login'))
        else:
            flash("⚠ Invalid email or password!", "danger")

    return render_template('login.html')


# ✅ **User Logout**
@app.route('/logout')
def logout():
    session.clear()
    flash("✅ Logout successful!", "info")
    return redirect(url_for('login'))

# ✅ **Admin Dashboard**
@app.route('/Export_manager_dashboard')
def Export_Manager_dashboard():
    if 'user_id' not in session or session.get('role') != 'Export_Manager':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM orders''')
    orders = cursor.fetchall()
    conn.close()

    return render_template('Export_Manager_dashboard.html', orders=orders)


# ✅ Generate Documents
@app.route('/generate_documents/<int:order_id>')
def generate_documents(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT orders.id, orders.vendor, orders.total_amount, orders.status, users.name AS customer_name 
        FROM orders 
        JOIN users ON orders.user_id = users.id 
        WHERE orders.id = ?
    ''', (order_id,))
    order = cursor.fetchone()

    cursor.execute('''
        SELECT products.name, order_items.quantity, order_items.price 
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
    ''', (order_id,))
    items = cursor.fetchall()
    conn.close()

    if order:
        order_dict = dict(order)
        order_dict['items'] = [dict(item) for item in items]

        for doc_type in ["invoice", "bill_of_lading", "shipping_label", "insurance_certificate"]:
            file_path = os.path.join(DOCUMENTS_FOLDER, f"{doc_type}_order_{order_id}.pdf")
            create_pdf(file_path, doc_type, order_dict)

        flash("✅ Documents generated successfully!", "success")
        return redirect(url_for('Export_Manager_dashboard'))

    return "Order not found", 404

# ✅ Function to Create PDF
# ✅ Function to Create Unique PDFs for Each Document Type
from fpdf import FPDF

# ✅ Function to Create Unique PDFs for Each Document Type
def create_pdf(file_path, doc_type, order):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=14)  # Bold Title
    pdf.cell(200, 10, f"{doc_type.replace('_', ' ').title()}", ln=True, align="C")
    pdf.ln(10)

    # Common Details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Order ID: {order['id']}", ln=True)
    pdf.cell(200, 10, f"Vendor: {order['vendor']}", ln=True)
    pdf.cell(200, 10, f"Customer: {order['customer_name']}", ln=True)
    pdf.cell(200, 10, f"Total Amount: Rs. {order['total_amount']}", ln=True)
    pdf.cell(200, 10, f"Status: {order['status']}", ln=True)
    pdf.ln(5)

    if doc_type == "invoice":
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, "Invoice Details:", ln=True)
        pdf.cell(200, 10, "--------------------------------------", ln=True)
        pdf.set_font("Arial", size=12)
        for item in order['items']:
            pdf.cell(200, 10, f"{item['name']} - Qty: {item['quantity']} - Rs. {item['price']}", ln=True)
        pdf.ln(5)
        pdf.cell(200, 10, "Thank you for your purchase!", ln=True, align="C")

    elif doc_type == "bill_of_lading":
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, "Shipping Details:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Carrier: XYZ Logistics", ln=True)
        pdf.cell(200, 10, "Ship Date: 2025-04-02", ln=True)
        pdf.cell(200, 10, "Destination: Customer Address", ln=True)
        pdf.cell(200, 10, "--------------------------------------", ln=True)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, "Shipping Items:", ln=True)
        pdf.set_font("Arial", size=12)
        for item in order['items']:
            pdf.cell(200, 10, f"{item['name']} - Qty: {item['quantity']}", ln=True)
        pdf.ln(5)
        pdf.cell(200, 10, "Handle with care!", ln=True, align="C")

    elif doc_type == "shipping_label":
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, "Shipping Label", ln=True)
        pdf.cell(200, 10, "--------------------------------------", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Sender: Vendor Warehouse", ln=True)
        pdf.cell(200, 10, f"Recipient: {order['customer_name']}", ln=True)
        pdf.cell(200, 10, "Tracking Number: TRK123456789", ln=True)
        pdf.cell(200, 10, "--------------------------------------", ln=True)
        pdf.cell(200, 10, "Fragile - Handle with Care!", ln=True, align="C")

    elif doc_type == "insurance_certificate":
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, "Insurance Certificate", ln=True)
        pdf.cell(200, 10, "--------------------------------------", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Insured By: ABC Insurance Co.", ln=True)
        pdf.cell(200, 10, f"Policy Number: INS-{order['id']}", ln=True)
        pdf.cell(200, 10, "Coverage Amount: Rs. 50,000", ln=True)
        pdf.cell(200, 10, "--------------------------------------", ln=True)
        pdf.cell(200, 10, "Insurance valid for damages during transit", ln=True, align="C")

    pdf.output(file_path, "F")

# ✅ View Documents
@app.route('/view_documents/<int:order_id>')
def view_documents(order_id):
    files = {
        "Invoice": f"invoice_order_{order_id}.pdf",
        "Bill of Lading": f"bill_of_lading_order_{order_id}.pdf",
        "Shipping Label": f"shipping_label_order_{order_id}.pdf",
        "Insurance Certificate": f"insurance_certificate_order_{order_id}.pdf",
    }

    return render_template("view_documents.html", files=files, order_id=order_id)

# ✅ Download Documents
@app.route('/download_document/<filename>')
def download_document(filename):
    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
    if not os.path.exists(file_path):
        flash("⚠ Document not found!", "danger")
        return redirect(url_for('Export_Manager_dashboard'))
    return send_file(file_path, as_attachment=True)

# ✅ **Vendor Dashboard**
@app.route('/vendor_dashboard')
def vendor_dashboard():
    if 'user_id' not in session or session.get('role') != 'vendor':
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')  # Fetch all products
    products = cursor.fetchall()
    conn.close()

    return render_template('vendor_dashboard.html', products=products) #pass the products to the template.


# @app.route('/')
# def home():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM products')
#     products = cursor.fetchall()
#     conn.close()
#     return render_template('index.html', products=products)

# ... (rest of the registration, login, logout, dashboards remain the same) ...

# ✅ **Add to Cart**
# ✅ **Add to Cart**
# ✅ **Add to Cart**
# ✅ **Add to Cart**

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session or session.get('role') != 'vendor':
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))

    quantity = int(request.form['quantity'])
    vendor_name = session.get('user_name')

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch product details
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()

    if product:
        price = float(product['price'])
        total_amount = price * quantity

        # ✅ Check if an order already exists with 'Pending' status
        cursor.execute('''
            SELECT id FROM orders WHERE user_id = ? AND status = 'Pending' AND vendor = ?
        ''', (session['user_id'], vendor_name))
        existing_order = cursor.fetchone()

        if existing_order:
            order_id = existing_order['id']  # ✅ Use existing order ID
        else:
            # ✅ Create a new order if no pending order exists
            cursor.execute('''
                INSERT INTO orders (user_id, total_amount, vendor, status, order_date)
                VALUES (?, ?, ?, 'Pending', CURRENT_TIMESTAMP)
            ''', (session['user_id'], total_amount, vendor_name))
            order_id = cursor.lastrowid  # Get the new order ID

        # ✅ Insert the product into the `order_items` table
        cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, product_id, quantity, price))

        conn.commit()
        flash("✅ Product added to cart!", "success")

    else:
        flash("⚠ Product not found!", "danger")

    conn.close()
    return redirect(url_for('vendor_dashboard'))

@app.route('/cart')
def view_cart():
    if 'user_id' not in session or session.get('role') != 'vendor':
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))

    vendor_name = session.get('user_name')  # ✅ Get vendor name

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch only "Pending" orders for the logged-in vendor
    cursor.execute('''
        SELECT o.id, oi.quantity, oi.price, p.name
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.vendor = ? AND o.status = 'Pending'
    ''', (vendor_name,))

    cart_items = cursor.fetchall()

    # ✅ Calculate total price only for the cart (Pending orders)
    total_price = sum(item['quantity'] * item['price'] for item in cart_items)

    conn.close()

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session:
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))

    vendor_name = session.get('user_name')

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch the "Pending" order for this vendor
    cursor.execute('''
        SELECT id FROM orders WHERE user_id = ? AND status = 'Pending' AND vendor = ?
    ''', (session['user_id'], vendor_name))
    order = cursor.fetchone()

    if not order:
        flash("⚠ No items in cart!", "danger")
        return redirect(url_for('view_cart'))

    order_id = order['id']

    # ✅ Fetch only the cart items (Pending order)
    cursor.execute('''
        SELECT oi.quantity, oi.price
        FROM order_items oi
        WHERE oi.order_id = ?
    ''', (order_id,))
    
    cart_items = cursor.fetchall()
    total_price = sum(item['quantity'] * item['price'] for item in cart_items)

    if request.method == "POST":
        # ✅ Change order status to Confirmed
        cursor.execute("UPDATE orders SET status = 'Confirmed' WHERE id = ?", (order_id,))

        conn.commit()
        flash("✅ Payment Successful! Order Confirmed. Your cart is now empty.", "success")
        return redirect(url_for('view_orders'))

    conn.close()
    return render_template('payment.html', total_price=total_price, success=False)

@app.route('/orders')
def view_orders():
    if 'user_id' not in session or session.get('role') != 'vendor':
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))

    vendor_name = session.get('user_name')

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch orders with status for the logged-in vendor
    cursor.execute('''
        SELECT o.id, o.total_amount, o.status, oi.quantity, p.name
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.vendor = ?
    ''', (vendor_name,))

    orders = cursor.fetchall()
    conn.close()

    return render_template('vendor_orders.html', orders=orders)



@app.route("/logistics_dashboard")
def logistics_dashboard():
    if session.get("role") != "logistics":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status != 'shipped'")
    orders = cursor.fetchall()
    conn.close()

    return render_template("logistics_dashboard.html", orders=orders)
@app.route('/documents/<filename>')
def serve_document(filename):
    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
    if not os.path.exists(file_path):
        flash("⚠ Document not found!", "danger")
        return redirect(url_for('logistics_dashboard'))
    return send_file(file_path, as_attachment=False)

@app.route("/mark_shipped/<int:order_id>")
def mark_shipped(order_id):
    if session.get("role") != "logistics":
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Update order status from 'Confirmed' to 'Shipped'
    cursor.execute("UPDATE orders SET status = 'Shipped' WHERE id = ?", (order_id,))
    
    conn.commit()  # ✅ Save changes
    conn.close()  # ✅ Close connection

    flash("✅ Order marked as shipped!", "success")
    return redirect(url_for("logistics_dashboard"))


if __name__ == '__main__':
    app.run(debug=True)
