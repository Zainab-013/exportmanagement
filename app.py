from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
import bcrypt
import sqlite3

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
            if user['role'] == "admin":
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == "vendor":
                return redirect(url_for('vendor_dashboard'))
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
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# ✅ **Vendor Dashboard**
@app.route('/vendor_dashboard')
def vendor_dashboard():
    if 'user_id' not in session or session.get('role') != 'vendor':
        flash("⚠ Unauthorized access!", "danger")
        return redirect(url_for('login'))
    return render_template('vendor_dashboard.html')

# ✅ **Product Management** (Add/Delete Products)
# ✅ **Add Product**
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    name = request.form['name']
    price = request.form['price']
    vendor = request.form['vendor']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price, vendor) VALUES (?, ?, ?)', (name, price, vendor))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Product added successfully'})

# ✅ **Edit Product**
@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    name = request.form['name']
    price = request.form['price']
    vendor = request.form['vendor']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET name=?, price=?, vendor=? WHERE id=?', (name, price, vendor, product_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Product updated successfully'})

# ✅ **Delete Product**
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Product deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
