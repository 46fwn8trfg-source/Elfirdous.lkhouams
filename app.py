import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'al_firdous_nature_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# إعداد قاعدة البيانات الجديدة لدعم الصور
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, phone TEXT, address TEXT, product TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, price TEXT, description TEXT, image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    prods = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=prods)

# رابط للوصول للصور المرفوعة وعرضها
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/order', methods=['POST'])
def make_order():
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    product = request.form['product']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (name, phone, address, product) VALUES (?, ?, ?, ?)', (name, phone, address, product))
    conn.commit()
    conn.close()
    return "<h1><center>شكراً لك! تم استلام طلبك بنجاح، سنتصل بك قريباً لتأكيد الشحن.</center></h1>"

@app.route('/admin_panel')
def admin():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY id DESC')
    ords = cursor.fetchall()
    cursor.execute('SELECT * FROM products ORDER BY id DESC')
    prods = cursor.fetchall()
    conn.close()
    return render_template('admin.html', orders=ords, products=prods)

@app.route('/add_product', methods=['POST'])
def add_product():
    title = request.form['title']
    price = request.form['price']
    description = request.form['description']
    file = request.files['image']
    
    filename = ""
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (title, price, description, image_path) VALUES (?, ?, ?, ?)', 
                   (title, price, description, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/delete_product/<int:id>')
def delete_product(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)

