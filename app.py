from flask import Flask, render_template, url_for, redirect, request, session, flash
from models import *
from datetime import datetime


@app.route('/')
def index():
    return render_template('Grocerystore.html')

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == "GET":
        return render_template("signup.html")
    
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            new_user = User(name=name, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['user_name'] = new_user.name
            session['user_id'] = new_user.id
            flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_name'] = user.name
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            print('Login failed. Please check your username and password.', 'danger')
            return redirect(url_for('login'))
    

# -----------------------ADMIN ROUTES-------------------------#

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' in session:
        categories = Category.query.all()
        products = Product.query.all()

        category_products = {}

        for category in categories:
            products = Product.query.filter_by(category=category).all()
            category_products[category] = products

        return render_template('admin_dashboard.html', categories=categories, category_products=category_products)
    
    else:
        return redirect(url_for('login'))


@app.route('/category/add', methods=['GET', 'POST'])
def add_category():
    if 'admin' in session:
        if request.method == "POST":
            category_name = request.form.get('categoryName')
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('category&product/add_category.html')
    else:
        return redirect(url_for('login'))

@app.route('/category/add_products/<int:category_id>', methods=['GET', 'POST'])
def add_products(category_id):
    if 'admin' in session:
        category = Category.query.get(category_id)

        if request.method == "POST":
            product_name = request.form.get('productName')
            mfg_date_str = request.form.get('mfgDate')
            price = request.form.get('price')
            quantity = request.form.get('quantity')
            unit = request.form.get('unit')
            mfg_date = datetime.strptime(mfg_date_str, '%Y-%m-%d').date()

            
            new_product = Product(name=product_name, mfg_date=mfg_date, price=price, quantity=quantity, unit=unit, category=category)
            db.session.add(new_product)
            db.session.commit()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin_dashboard')) 
        
        return render_template('category&product/add_products.html', category=category)
    else:
        return redirect(url_for('login'))

@app.route('/category/delete/<int:category_id>', methods=['GET', 'POST'])
def delete_category(category_id):
    if 'admin' in session:
        category = Category.query.get(category_id)
        
        if category:
            products = Product.query.filter_by(category_id=category_id).all()
            for product in products:
                db.session.delete(product)

            db.session.delete(category)
            db.session.commit()
            flash('Category deleted successfully!', 'success')
        else:
            flash('Category not found.', 'danger')

        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if 'admin' in session:
        category = Category.query.get(category_id)

        if request.method == 'POST':
            new_category_name = request.form.get('newCategoryName')
            if category:
                category.name = new_category_name
                db.session.commit()
                flash('Category edited successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Category not found', 'danger')

        return render_template('category&product/edit_category.html', category=category)
    else:
        return redirect(url_for('login'))

@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'admin' in session:
        product = Product.query.get(product_id)

        if request.method == 'POST':
            product.name = request.form.get('name')
            product.mfg_date = datetime.strptime(request.form.get('mfg_date'), '%Y-%m-%d').date()
            product.price = request.form.get('price')
            product.quantity = request.form.get('quantity')
            product.unit = request.form.get('unit')
            

            db.session.commit()
            flash('Product edited successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('category&product/edit_product.html', product=product)
    else:
        return redirect(url_for('login'))

@app.route('/product/delete/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    if 'admin' in session:
        product = Product.query.get(product_id)

        if request.method == 'POST':
            if product:
                db.session.delete(product)
                db.session.commit()
                flash('Product deleted successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Product not found', 'danger')

        return render_template('category&product/delete_product.html', product=product)
    else:
        return redirect(url_for('login'))

@app.route('/admin/logout')
def logout():
    if 'admin' in session:
        session.pop('admin', None)
        flash('Admin logged out successfully!', 'success')
    else:
        flash('Admin is not logged in.', 'danger')
    return redirect(url_for('index')) 

# -----------------------USER ROUTES-------------------------#

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_name' in session:
        user_name = session.get('user_name')
        categories = Category.query.all()
        products = Product.query.all()

        category_products = {}

        for category in categories:
            products = Product.query.filter_by(category=category).all()
            category_products[category] = products

        return render_template('user_templates/user_dashboard.html', user_name=user_name,categories=categories, category_products=category_products)
    else:
        return redirect(url_for('login'))


@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if 'user_name' in session:
        user_name = session.get('user_name')
        user_id = session.get('user_id') 
        product = Product.query.get(product_id)

        if not product:
            return "Product not found."

        total = 0 

        if request.method == 'POST':
            quantity = int(request.form.get('quantity'))
            price = float(request.form.get('price'))
            
            if product.quantity < quantity:
                return redirect(url_for('add_to_cart', product_id=product.id))  
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product.id).first()  

            if cart_item:
                if cart_item.quantity + quantity > product.quantity:
                    cart_item.quantity += quantity
                    product.quantity -= quantity
                    db.session.commit
                    return redirect(url_for('cart'))

                cart_item.quantity += quantity
            else:
                cart_item = Cart(user_id=user_id, product_id=product.id, quantity=quantity)
                db.session.add(cart_item)
                
            product.quantity -= quantity
            total = quantity * price
            db.session.commit()
            return redirect(url_for('cart'))

        price_per_unit = product.price
        return render_template('user_templates/buy_product.html', user_name=user_name, product=product, price_per_unit=price_per_unit, total=total)
    else:
        return redirect(url_for('login'))


@app.route('/search_product', methods=['POST'])
def search_product():
    if 'user_name' in session:
        user_name = session.get('user_name')
        categories = Category.query.all()
        search_query = request.form.get('search_query')
        category_products = {}

        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()

        return render_template('user_templates/search_results.html', user_name=user_name, search_results=products, categories=categories, category_products=category_products)
    else:
        return redirect(url_for('login'))


@app.route('/cart')
def cart():
    if 'user_name' in session:
        user_name = session.get('user_name')
        user_id = session.get('user_id')

        
        cart_items = Cart.query.filter_by(user_id=user_id).all()

        cart_details = []
        total_price = 0

        for cart_item in cart_items:
            
            product = Product.query.get(cart_item.product_id)

            
            total = cart_item.quantity * product.price

            
            cart_detail = {
                'cart_item': cart_item,
                'product': product,
                'total': total
            }

            cart_details.append(cart_detail)
            total_price += total

        return render_template('user_templates/cart.html', user_name=user_name, cart_details=cart_details, total_price=total_price)
    else:
        return redirect(url_for('login'))


@app.route('/thank_you', methods=['GET', 'POST'])
def thank_you():
    if 'user_name' in session:
        user_name = session.get('user_name')
        user_id = session.get('user_id')

        cart_items = Cart.query.filter_by(user_id=user_id).all()
        order_items = []

        total_order_price = 0
        order_date_time = datetime.now()

        if request.method == 'POST':
            for cart_item in cart_items:
                product = Product.query.get(cart_item.product_id)

                total_item_price = cart_item.quantity * product.price
                order_item = {
                    'cart_item': cart_item,
                    'product': product,
                    'total_item_price': total_item_price
                }

                order_items.append(order_item)
                total_order_price += total_item_price

            for cart_item in cart_items:
                db.session.delete(cart_item)

            db.session.commit()

            return render_template('user_templates/thank_you.html', user_name=user_name, order_items=order_items, total_order_price=total_order_price, order_date_time=order_date_time)

        return render_template('user_templates/cart.html', user_name=user_name, cart_items=cart_items, total_order_price=total_order_price, order_date_time=order_date_time)
    else:
        return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'user_name' in session:
        user_name = session.get('user_name')
        username = session.get('username')  
        return render_template('profile.html', user_name=user_name, username=username)
    else:
        return redirect(url_for('login'))



@app.route('/user/logout')
def user_logout():
    if 'user_name' in session:
        session.pop('user_name', None)
        flash('Logged out successfully!', 'success')
    else:
        flash('You are not logged in.', 'danger')
    return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.secret_key = 'projectsecretkey' 
    app.run(debug=True)
