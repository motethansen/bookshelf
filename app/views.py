from app import app, lm
from flask import request, redirect, render_template, url_for, flash, json
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .forms import LoginForm, SignupForm
from .user import User
from flask_principal import Principal, Permission, RoleNeed
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed
import os
import uuid
from flask_paginate import Pagination, get_page_parameter, get_page_args


# class ShoppingCart():
#
#     def __init__(self):
#         self.total = 0
#         self.items = dict()
#
#     def add_item(self, item_name, quantity, price):
#         """This method should adds the cost of the added items to the current value of total , and
#         also adds an entry to the items dict such that the key is the item_name and the value is the quantity of the item """
#         self.total = self.total + (price * quantity)
#         self.items[item_name] = quantity
#
#     def remove_item(self, item_name, quantity, price):
#         """remove items that have been added to the shopping cart and are not required, and
#              deduct the cost of the removed items from the current total"""
#         # get remaining quantity of item to be removed in items
#         quantityLeft = self.items[item_name]
#
#         # checkk if its greater than the quantity to be removed
#         if quantityLeft > quantity:
#             # reduce the quantity
#             self.items[item_name] = self.items[item_name] - quantity
#             # reduce the total cost
#             self.total = self.total - (price * quantity)
#         else:
#             # assume the item is nolonger needed, delete it from items
#             self.total = self.total - (price * quantityLeft)
#             self.items.pop(item_name)
#
#     def checkout(self, cash_paid):
#         """ return the customer's balance"""
#         # if cash paid is less than total
#         if cash_paid < self.total:
#             return "Cash paid not enough"
#         else:
#             return cash_paid - self.total

# load the extension
principals = Principal(app)

#login_manager = LoginManager(app)

#@login_manager.user_loader
def load_user(userid):
    # Return an instance of the User model
    user = app.config['USERS_COLLECTION'].find_one({"_id": userid})
    return user['_id']

def load_useremail(userid):
    #return the current user email
    user = app.config['USERS_COLLECTION'].find_one({"_id": userid})
    return user['email']

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))

# Create a permission with a single Need, in this case a RoleNeed.
user_permission = Permission(RoleNeed('user'))

def dbCheck():
    bookcounts = app.config['BOOKIMPORT_COLLECTION'].count()
    print ('bookcounts :' + str(bookcounts))
    return bookcounts


def get_css_framework():
    return 'bootstrap4'


def get_link_size():
    return 'sm'  # option lg


def get_user():
    return current_user.get_id()


# protect a view with a principal for that need
@app.route('/admin')
@admin_permission.require()
def do_admin_index():
    return Response('Only if you are an admin')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route("/home", methods=['GET'])
@app.route("/index", methods=['GET'])
@app.route("/", methods=['GET'])
def home():
    PER_PAGE = 48
    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    booksimported = dbCheck()

    # get_page_arg defaults to page 1, per_page of 10
    page, per_page, offset = get_page_args()
    # page = request.args.get(get_page_parameter(), type=int, default=1)

    # booksInLibrary = app.config['LIBRARY_COLLECTION'].count()
    # bookLibrary = app.config['LIBRARY_COLLECTION'].find()
    booksInLibrary = app.config['BOOKIMPORT_COLLECTION'].count()
    bookLibrary = app.config['BOOKIMPORT_COLLECTION'].find()
    i = (page - 1) * PER_PAGE
    List1 = bookLibrary[i:i + PER_PAGE]
    # return render_template('index.html', books=bookLibrary, booksimported= booksimported, booksInLibrary=booksInLibrary)
    # return render_template('home.html')
    pagination = Pagination(css_framework=get_css_framework(), link_size=get_link_size(), page=page, per_page=PER_PAGE,
                            total=booksInLibrary, search=search, record_name='bookLibrary')
    # 'page' is the default name of the page parameter, it can be customized
    # e.g. Pagination(page_parameter='p', ...)
    # or set PAGE_PARAMETER in config file
    # also likes page_parameter, you can customize for per_page_parameter
    # you can set PER_PAGE_PARAMETER in config file
    # e.g. Pagination(per_page_parameter='pp')

    # mycart = ShoppingCart()

    return render_template('index.html',
                           books=List1,
                           booksimported=booksimported,
                           booksInLibrary=booksInLibrary,
                           pagination=pagination  # ,
                           # cart = mycart
                           )


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = ShoppingCart.get()
    return render_template("cart.html", cart=cart)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    print ("Enter signup form ") + form.username.data
    if request.method == 'POST':  # and form.validate_on_submit():
        # check if user_name or email is taken
        print ("look up user %s") + form.username.data
        user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
        print ("value of user search ") + str(user)
        if user and User.validate_login(user['password'], form.password.data):
            flash("User already exist!", category='error')
            return render_template('signup.html', title='Register', form=form)

        try:
            # create new user
            pass_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            app.config['USERS_COLLECTION'].insert_one(
                {"_id": form.username.data, "password": pass_hash, "name": form.first_name.data,
                 "surname": form.last_name.data, "email": form.email.data})
            # log the user in
            user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("dashboard"))
        except Exception as e:
            print ("exception.") + e

    return render_template('signup.html', title='Register', form=form)


@app.route("/productDescription", methods=['GET', 'POST'])
# @login_required
def productDescription():
    # loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    # search the mongodb for the product
    print ("sku :") + str(productId)

    bookdetails = app.config['LIBRARY_COLLECTION'].find_one({"sku": productId})
    print ('bookdetails :') + bookdetails.title
    return render_template("productDescription.html", data=bookdetails, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    print ("user :",  get_user())
    return render_template('dashboard.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


@lm.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])


@app.route("/updatebooks", methods=['GET'])
def updateBookshelf():
    # get bookshelf library
    booksInLibrary = app.config['LIBRARY_COLLECTION'].count()
    # get all the document in bookimports
    cursor = app.config['BOOKIMPORT_COLLECTION'].find({})
    for document in cursor:
        uniqueID = uuid.uuid1()
        document['sku'] = uniqueID
        app.config['LIBRARY_COLLECTION'].insert(document)

    return redirect("/")


@app.route("/bookform", methods=['POST', 'GET'])
def bookform():
    booksimported = dbCheck()
    booksInLibrary = app.config['LIBRARY_COLLECTION'].count()

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        ISBN = request.form.get('ISBN')
        price = request.form.get('price')
        description = request.form.get('description')
        book = dict(title=title, author=author, published='', ISBN=ISBN, image='', price=price, description=description,
                    category='')
        oid = app.config['LIBRARY_COLLECTION'].insert(book)
    return render_template("/bookform.html", booksimported=booksimported, booksInLibrary=booksInLibrary)


@app.route("/update", methods=['POST'])
def update():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        ISBN = request.form.get('ISBN')
        price = request.form.get('price')
        description = request.form.get('description')
        book = dict(title=title, author=author, published='', ISBN=ISBN, image='', price=price, description=description,
                    category='')
        oid = app.config['LIBRARY_COLLECTION'].insert(book)
    return redirect("/")


@app.route("/deleteall", methods=['GET'])
def deleteall():
    app.config['LIBRARY_COLLECTION'].remove()
    return redirect("/")
