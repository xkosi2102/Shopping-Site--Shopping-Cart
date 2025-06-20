from flask import Flask, render_template, session, redirect, url_for, request, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'replace_with_a_secure_key'

# User data file
USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def persist_cart():
    username = session.get('username')
    if not username:
        return
    users = load_users()
    users.setdefault(username, {})
    users[username]['cart'] = session.get('cart', {})
    save_users(users)

from products import products

@app.route('/')
def index():
    # preia filtrele
    cat    = request.args.get('category', 'all')
    sort   = request.args.get('sort', '')
    search = request.args.get('search', '').strip().lower()

    # filtrare pe categorie
    prods = [p for p in products if cat=='all' or p['category']==cat]

    # filtrare pe termen de căutare (nume sau descriere)
    if search:
        prods = [
          p for p in prods
          if search in p['name'].lower() or search in p['description'].lower()
        ]

    # sortare
    if sort=='price_asc':
        prods.sort(key=lambda p: p['price'])
    elif sort=='price_desc':
        prods.sort(key=lambda p: p['price'], reverse=True)
    elif sort=='rating':
        prods.sort(key=lambda p: p['rating'], reverse=True)

    categories = ['all','men','women']
    return render_template('index.html',
                           products=prods,
                           categories=categories,
                           selected_category=cat,
                           selected_sort=sort,
                           search=search)

@app.route('/product/<id>')
def product_detail(id):
    prod = next((p for p in products if p['id'] == id), None)
    if not prod:
        return render_template('404.html'), 404
    return render_template('product.html', product=prod)

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        prod = next((p for p in products if p['id'] == pid), None)
        if prod:
            item_total = prod['price'] * qty
            items.append({'product': prod, 'quantity': qty, 'total': item_total})
            total += item_total
    return render_template('cart.html', items=items, total=total)

@app.route('/cart/add-item/')
def add_item():
    pid = request.args.get('id')
    if pid:
        cart = session.get('cart', {})
        cart[pid] = cart.get(pid, 0) + 1
        session['cart'] = cart
        persist_cart()
    return redirect(url_for('cart'))

@app.route('/cart/remove-item')
def remove_item():
    pid = request.args.get('id')
    cart = session.get('cart', {})
    if pid in cart:
        cart.pop(pid)
        session['cart'] = cart
        persist_cart()
    return redirect(url_for('cart'))

@app.route('/cart/update-item', methods=['POST'])
def update_item():
    pid = request.form.get('id')
    action = request.form.get('action')
    cart = session.get('cart', {})
    if pid in cart:
        if action == 'increment':
            cart[pid] += 1
        elif action == 'decrement':
            cart[pid] = max(1, cart[pid] - 1)
        elif action == 'update':
            try:
                qty = int(request.form.get('quantity', 1))
                if qty > 0:
                    cart[pid] = qty
                else:
                    cart.pop(pid)
            except ValueError:
                pass
    session['cart'] = cart
    persist_cart()
    return redirect(url_for('cart'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        users = load_users()
        if not username or username in users:
            flash('Username invalid or already exists', 'danger')
        else:
            users[username] = {
                'password': password,
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'address': address
            }
            save_users(users)
            session['username'] = username
            flash('Account created', 'success')
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()
        user = users.get(username)
        if user and user.get('password') == password:
            session['username'] = username
            session['cart'] = users.get(username, {}).get('cart', {})
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    # clear only the session cart 
    session.pop('cart', None)
    session.pop('username', None)
    return redirect(url_for('index'))

def get_cart_items():
    cart = session.get('cart', {})
    items = []
    for pid, qty in cart.items():
        prod = next((p for p in products if p['id'] == pid), None)
        if prod:
            item_total = prod['price'] * qty
            items.append({'product': prod, 'quantity': qty, 'total': item_total})
    return items

def compute_total(items):
    return sum(item['total'] for item in items)

def load_user_data():
    if session.get('username'):
        users = load_users()
        return users.get(session['username'])
    return None

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    
    raw = session.get('cart', [])
    items = []
    total = 0
    for entry in raw:
        if isinstance(entry, dict):
            pid = entry.get('id')
            qty = entry.get('quantity', 1)
        else:
            pid = entry
            qty = 1
        prod = next((p for p in products if p['id'] == pid), None)
        if not prod:
            continue
        line_total = prod['price'] * qty
        items.append({'product': prod, 'quantity': qty, 'total': line_total})
        total += line_total

    if request.method == 'POST':
        order_data = {
            'full_name':      request.form['full_name'],
            'email':          request.form['email'],
            'phone':          request.form['phone'],
            'address':        request.form['address'],
            'payment_method': request.form['payment_method'],
            'items':          items,
            'total':          total,
            'timestamp':      datetime.utcnow().isoformat()
        }
        print('=== New Order ===\n', json.dumps(order_data, indent=2))
        with open('orders.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(order_data) + "\n")
        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('index'))

    user = load_user_data()
    return render_template('checkout.html',
                           items=items,
                           total=total,
                           user=user)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
