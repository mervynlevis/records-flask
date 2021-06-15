"""
There are users and admin users. The admin user is entered into the database. 
To access the admin features page, sign is with user_id "admin" and password "admin".
Use the /admin route to access the admin page of the app.
Search by artist, or check the stock page for the full stock. Login to check your profile to see your past orders and reviews.

"""

from flask import Flask, render_template, request, session, redirect, url_for, make_response, g
from database import get_db, close_db
from forms import RegisterForm, SearchForm, LoginForm, AddStockForm, ReviewForm, RemoveStockForm, EditStockForm, AddUserForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from functools import wraps
from datetime import date 

# NEW

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)


@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(**kwargs)
    return wrapped_view


@app.route("/", methods =["GET", "POST"])
def start():
    title = "Home"
    form = SearchForm()
    stock = None
    db = get_db()
    user_id = "admin"
    password = "admin"
    print("Hello")
    if db.execute("""SELECT * FROM users WHERE user_id = ?;""",(user_id,)).fetchone() is None:
        db.execute("""INSERT INTO users (user_id, password) VALUES (?, ?);""",(user_id, generate_password_hash(password)))
        db.commit()
        print("admin user added to users")
    else:
        print("admin user already in users table, not added")

    if form.validate_on_submit():
        stock = form.search.data
        stock = stock.lower()
        db = get_db()
        stock = db.execute("""SELECT * FROM records WHERE artist = ?;""",(stock,)).fetchall()

    # GET RANDOM RECORD RECOMMENDATIONS

    rec_record_id = db.execute("""SELECT * FROM records ORDER BY RANDOM() LIMIT 8;""")
    print(rec_record_id)

    return render_template("index.html", title=title, form=form, stock=stock, rec_record_id=rec_record_id, caption="Stock")


@app.route("/record/<int:record_id>", methods =["GET", "POST"])
def record(record_id):
    db = get_db()
    leave_review = ""
    records = db.execute("""SELECT * FROM records WHERE record_id = ?;""",(record_id,)).fetchone()
    reviews = db.execute("""SELECT * FROM reviews WHERE record_id = ?;""",(record_id,)).fetchall()
    artist = db.execute("""SELECT artist FROM records WHERE record_id = ?;""",(record_id,)).fetchone()["artist"]
    record_title = db.execute("""SELECT title FROM records WHERE record_id = ?;""",(record_id,)).fetchone()["title"] #advise from Derek Bridge
    form = ReviewForm()

    if form.validate_on_submit():
        review = form.review.data
        stars = form.stars.data
        record_id = str(record_id)
        leave_review = db.execute("""INSERT INTO reviews (record_id, artist, title, user_id, review, stars) VALUES (?, ?, ?, ?, ?, ?);""",(record_id, artist, record_title, g.user, review, stars))
        db.commit()
        return redirect(url_for("record", record_id=record_id, leave_review=leave_review))

    return render_template("record.html", records=records, form=form, reviews=reviews, leave_review=leave_review)

@app.route("/artist/<artist>")
def artist(artist):
    db = get_db()
    records = db.execute("""SELECT * FROM records WHERE artist = ?;""",(artist,)).fetchall()
    reviews = db.execute("""SELECT * FROM reviews WHERE artist = ?;""",(artist,)).fetchall()
    title = artist
    print(records)
    print("HELLO")
    return render_template("artist.html", title=title, artist=artist, records=records, reviews=reviews)


@app.route("/stock", methods =["GET", "POST"])
def stock():
    title = "Stock"
    db = get_db()
    instock = 1
    stock = db.execute("""SELECT * FROM records WHERE stock >= ?;""",(instock,)).fetchall()
    out_of_stock = db.execute("""SELECT * FROM records WHERE stock < ?;""",(instock,)).fetchall()
    return render_template("stock.html", caption="Stock", stock=stock, out_of_stock=out_of_stock, title=title)


@app.route("/register", methods =["GET", "POST"])
def register():
    title = "Register"
    today = date.today()
    signup_date = today.strftime("%B %d, %Y")
    print(signup_date)
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()

        if db.execute("""SELECT * FROM users WHERE user_id = ?""", (user_id,)).fetchone() is not None:
            form.user_id.errors.append("User id already registered")
        else:
            db.execute("""INSERT INTO users (user_id, password, signup_date) VALUES (?, ?, ?);""", (user_id, generate_password_hash(password), signup_date))
            db.commit()

            return redirect( url_for("profile", signup_date=signup_date ))

    return render_template("register.html", form=form, title=title)


@app.route("/login", methods=["GET", "POST"])
def login():
    title = "Login"
    admin = False
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute("""SELECT * FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
        if user == "admin" and check_password_hash(user["password"], password):
            print("admin hello")
            admin = True
            return redirect( url_for("admin", admin=admin))
        elif user is None:
            form.user_id.errors.append("Unknown user id")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["user_id"] = user_id
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("stock")
            return redirect(next_page)
    return render_template("login.html", form=form, title=title, admin=admin)


@app.route("/logout")
def logout():
    goodbyeuser = g.user
    session.clear()
    return redirect(url_for("goodbye", goodbyeuser=goodbyeuser))


@app.route("/cart")
@login_required
def cart():
    title = "Your Cart"
    if "cart" not in session:
        session["cart"] = {}
    names = {}
    db = get_db()
    final_total = 0
    price = 0
    for record_id in session["cart"]:
        name = db.execute("""SELECT * FROM records WHERE record_id = ?;""", (record_id,)).fetchone()["title"]
        names[record_id] = name
        print("record name:",name)
        price = db.execute("""SELECT price FROM records WHERE record_id = ?;""", (record_id,)).fetchone()["price"]
        names[price] = price ###prices are the same, couldnt get the individual prices to work correctly
        print("record price:",names[price])

        cart_total = price.strip("€")

        cart_total = int(cart_total) *session["cart"][record_id]
        print("cart_total:",cart_total) 
        names[price] = cart_total
        print("record price total:",names[price])

        final_total += cart_total
    final_total = str(final_total)
    final_total = "€"+final_total
    print("final_total:",final_total)
    print("sessionCart:",session["cart"])
    print("names:",names)
    return render_template("cart.html", cart=session["cart"], title=title, names=names, price=price, final_total=final_total)


@app.route("/add_to_cart/<int:record_id>")
def add_to_cart(record_id):
    if "cart" not in session:
        session["cart"] = {}
    if record_id not in session["cart"]:
        session["cart"][record_id] = 0
    session["cart"][record_id] = session["cart"][record_id] + 1
    return redirect( url_for("cart", record_id=record_id))


@app.route("/remove_from_cart/<int:record_id>") 
def remove_from_cart(record_id):
    print("record id =",record_id)
    print("session_cart =",session['cart'])
    cart = session['cart']
    db = get_db()
    numRecords = db.execute("""SELECT * FROM records;""").fetchall() #using this to get length of all record ids
    print(numRecords)
    for record in numRecords:
        print("record id now",record_id)
        if record_id in cart:
            cart.pop(record_id)
            return redirect( url_for("cart"))
        record_id += 1
    return redirect( url_for("cart"))

@app.route("/empty_cart")
def empty_cart():
    db = get_db()
    print("sessionCart = ",session["cart"])
    user_id = g.user
    order = ""
    item = ""
    total_price = 0
    orders = db.execute("SELECT * FROM orders WHERE user_id = ?;""",(user_id,)).fetchall()
    
    for record in session["cart"]:
        print(record)
        quantity = session["cart"][record]
        print("Quantity =",quantity)
        artist = db.execute("""SELECT artist FROM records WHERE record_id = ?;""",(record,)).fetchone()["artist"]
        artist = artist + " : "
        title = db.execute("""SELECT title FROM records WHERE record_id = ?;""",(record,)).fetchone()["title"]
        record_format = db.execute("""SELECT format FROM records WHERE record_id = ?;""",(record,)).fetchone()["format"]
        record_format = " ("+record_format+")"
        price = db.execute("""SELECT price FROM records WHERE record_id = ?;""",(record,)).fetchone()["price"]
        price = price.lstrip('€')
        price = int(price)
        print("price =",price)
        item = artist + title + record_format
        item = str(item)
        print("item =",item)
        total_price += price
        order = order + '\n' + item  + '\n' #cant get this line break in the html table

        # updating stock number
        record_id = db.execute("""SELECT record_id FROM records WHERE record_id =?;""",(record,)).fetchone()["record_id"]
        print("record_id =",record_id)
        stock = db.execute("""SELECT stock FROM records WHERE record_id = ?;""",(record,)).fetchone()["stock"]
        print("Stock =",stock)
        updatedStock = stock - quantity
        print("Updated stock =",updatedStock)

        if updatedStock <= 0:
            print("record out of stock")
            updatedStock = 0

        db.execute("""UPDATE records SET stock = ? WHERE record_id = ?;""",(updatedStock, record,))
        db.commit()


    print("Full order is:",order)
    today = date.today()
    order_date = today.strftime("%B %d, %Y")
    order_date = str(order_date)
    print("Order date = ",order_date)
    intprice = price
    price = str(total_price)
    integerTotalPrice = int(total_price)
    price = "€"+price
    print("Total price =",price)
    order = str(order)
    print("Full order =",order)
    new_order = db.execute("""INSERT INTO orders (user_id, order_content, price, order_date) VALUES (?, ?, ?, ?);""",(user_id, order, price, order_date))
    db.commit()

    get_sales = db.execute("""SELECT * FROM sales;""").fetchone()["total_sales"]
    print("Old total sales:",get_sales)
    get_sales = int(get_sales)

    print("add:",integerTotalPrice)
    sales = integerTotalPrice + get_sales
    print("New total sales:",sales)
    # total_sales = str(total_price)
    # total_sales = total_sales
    # print("total sales:",total_sales)

    total_sales = db.execute("""UPDATE sales SET total_sales = ?;""",(sales,))
    db.commit()

    session["cart"].clear() #this clears the cart by clearing the cart session, leaves the user logged in
    return redirect(url_for("profile", new_order=new_order, orders=orders, total_sales=total_sales))


@app.route("/admin", methods =["GET", "POST"])
@login_required
def admin():
    if g.user == "admin2" or g.user == "admin":
        title = 'Admin features: add and remove stock, view all users etc'
        admin = "admin"

        db = get_db()
        
        users = db.execute("""SELECT * FROM users WHERE user_id != ?;""",(admin,)).fetchall()
        user_count = len(users)
        print("user count: ",user_count)
        # form = {{ url_for('add_stock') }} 
        # form2 = {{ url_for('remove_stock') }} 
        # form3 = {{ url_for('edit_stock') }}

        form = AddStockForm()
        form2 = RemoveStockForm()
        form3 = EditStockForm()
        form4 = AddUserForm()
        
        stock = db.execute("""SELECT * FROM records;""").fetchall()
        nostock = 0
        out_of_stock = db.execute("""SELECT * FROM records WHERE stock <= ?;""",(nostock,)).fetchall()
        orders = db.execute("""SELECT * FROM orders;""").fetchall()
        total_orders = len(orders)
        print("total orders:",total_orders)
        db.commit()

        total_sales = db.execute("""SELECT total_sales FROM sales;""").fetchone()["total_sales"]
        print("Total sales:",total_sales)

        return render_template("admin.html", form=form, form2=form2, form3=form3,  form4=form4, users=users, user_count=user_count, total_orders=total_orders, total_sales=total_sales, title=title, admin=admin, stock=stock, orders=orders, out_of_stock=out_of_stock)
    else:
        return redirect( url_for("login"))


@app.route("/add_stock", methods=['GET', 'POST'])
def add_stock():
    db = get_db()
    form = AddStockForm()
    if form.submit.data and form.validate_on_submit():
        title = form.title.data
        artist = form.artist.data
        length = form.length.data
        length = length + " min"
        price = form.price.data
        price = "€"+price
        stock = form.stock.data
        stockFormat = form.stockFormat.data
        new_stock = db.execute("""INSERT INTO records (title,artist,length,price,stock,format) VALUES (?,?,?,?,?,?);""",(title,artist,length,price,stock,stockFormat))
        db.commit()
        print("Add Stock:",new_stock)
        return redirect(url_for("admin"))


@app.route("/remove_stock", methods=['GET', 'POST'])
def remove_stock():
    db = get_db()
    form2 = RemoveStockForm()
    if form2.submit.data and form2.validate_on_submit():
        record_id = form2.record_id.data
        db.execute("""DELETE FROM records WHERE record_id = ?;""",(record_id,)).fetchone()
        db.commit()
        print("removed:",record_id)
        return redirect(url_for("admin"))


@app.route("/edit_stock", methods=['GET', 'POST'])
def edit_stock():
    db = get_db()
    form3 = EditStockForm()
    if form3.submit.data and form3.validate_on_submit():
        record_id = form3.record_id.data
        length = form3.length.data
        length = length + " min"
        price = form3.length.data
        price = "€"+price
        stock = form3.stock.data
        update_stock = db.execute("""UPDATE records SET length = ?, price = ?, stock = ? where record_id = ?;""",(length, price, stock, record_id))
        db.commit()
        print("update stock:",update_stock)
        print("its working")
        return redirect(url_for("admin"))

@app.route("/add_user", methods=['GET','POST'])
def add_user():
    db = get_db()
    form4 = AddUserForm()

    user_id = form4.user_id.data
    password = form4.password.data
    today = date.today()
    signup_date = today.strftime("%B %d, %Y")
    signup_date = str(signup_date)

    db.execute("""INSERT INTO users VALUES (?,?,?);""",(user_id, generate_password_hash(password), signup_date))
    db.commit()
    return redirect(url_for("admin")) 

@app.route("/delete_user/<user_id>", methods=['GET','POST'])
def delete_user(user_id):
    user_id = user_id
    db = get_db()
    if g.user == "admin" or g.user == "admin2":
        db.execute("""DELETE FROM users WHERE user_id = ?;""",(user_id,))
        db.commit()
        print("deleted user:",user_id)
        return redirect(url_for("admin"))

@app.route("/delete_your_account/<user_id>", methods=["GET","POST"])
def delete_your_account(user_id):
    # user_id = user_id
    # db = get_db()
    # db.execute("""DELETE FROM users WHERE user_id = ?;""",(user_id,))
    # db.commit()
    # print("Deleted your account:",user_id)
    return redirect( url_for("delete"))

@app.route("/delete_confirmation", methods=["GET","POST"])
def delete_confirm(user_id):
    return render_template("delete.html")


@app.route("/profile")
@login_required
def profile():
    title = "Profile"
    user_id = g.user
    db = get_db()
    reviews = db.execute("""SELECT * FROM reviews WHERE user_id = ?;""",(user_id,))
    orders = db.execute("""SELECT * FROM orders WHERE user_id =?""",(user_id,))
    register_date = db.execute("""SELECT signup_date FROM users WHERE user_id = ?;""",(user_id,))
    db.commit() 
    return render_template("profile.html", register_date=register_date, reviews=reviews, orders=orders, profile=profile, title=title)


@app.route("/goodbye")
def goodbye():
    return render_template("goodbye.html")

