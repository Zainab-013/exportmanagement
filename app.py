from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
import bcrypt  # Password hashing ke liye

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

        # ✅ Hash password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
            conn.commit()
            conn.close()
            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except:
            flash("⚠ Email already exists! Try a different one.", "danger")

    return render_template('register.html')

# ✅ **User Login**
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

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("✅ Login successful!", "success")
            return redirect(url_for('show_products'))
        else:
            flash("⚠ Invalid email or password!", "danger")

    return render_template('login.html')

# ✅ **User Logout**
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("✅ Logout successful!", "info")
    return redirect(url_for('login'))

# 🛒 **Products Page**
@app.route('/products')
def show_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=products)

# 📄 **Product Details**
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if product:
        return render_template('product_detail.html', product=product)
    else:
        return "Product Not Found", 404

# 🛒 **Add to Cart**
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if not product:
        return "Product Not Found", 404

    if 'cart' not in session:
        session['cart'] = []

    for item in session['cart']:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        session['cart'].append({
            'id': product_id,
            'name': product['name'],
            'price': float(product['price']),
            'quantity': 1
        })

    session.modified = True
    flash("Item added to cart!", "success")
    return redirect(url_for('show_cart'))

# 🛍️ **Show Cart**
@app.route('/cart')
def show_cart():
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item.get('quantity', 1) for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)

# 🔄 **Update Cart Quantity**
@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    new_quantity = int(request.form.get('quantity', 1))
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] = max(1, new_quantity)
                break
        session.modified = True
    return redirect(url_for('show_cart'))

# ❌ **Remove from Cart**
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
    return redirect(url_for('show_cart'))

# ❌ **Clear Cart**
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('show_cart'))

# ✅ **Checkout Page**
@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash("Cart is empty!", "warning")
        return redirect(url_for('show_products'))

    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price)

# ✅ **Process Checkout**
@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    name = request.form.get('name')
    address = request.form.get('address')
    payment_method = request.form.get('payment')

    if not name or not address or not payment_method:
        flash("Please fill all required fields!", "danger")
        return redirect(url_for('checkout'))

    cart = session.get('cart', [])
    if not cart:
        flash("Cart is empty!", "warning")
        return redirect(url_for('show_products'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Save Order to Database
    cursor.execute("INSERT INTO orders (name, address, payment_method, total_amount) VALUES (?, ?, ?, ?)",
                   (name, address, payment_method, sum(item['price'] * item['quantity'] for item in cart)))
    order_id = cursor.lastrowid

    # ✅ Save Ordered Items
    for item in cart:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                       (order_id, item['id'], item['quantity'], item['price']))

    conn.commit()
    conn.close()

    # 🛒 Clear Cart
    session.pop('cart', None)
    flash("Order Placed Successfully! ✅", "success")
    return redirect(url_for('show_products'))

if __name__ == '__main__':
    app.run(debug=True)
