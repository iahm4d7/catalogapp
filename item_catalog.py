from flask import Flask, render_template, request, redirect, jsonify, \
 url_for,  flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from database_setup import Category, Book, User, Base
from flask import session as login_session
import random
import string
import httplib2
import json
from flask import make_response
import requests
from forms import RegistrationForm, LoginForm



app = Flask(__name__)


# Connect to Database
engine = create_engine('sqlite:///books_catalog.db',
                       connect_args={'check_same_thread': False})

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('showLogin'))
        return render_template('register.html', title='Register', form=form)

@app.route('/login')
def showLogin():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('showCatalog'))
        else:
            flash('login unsuccessful, please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except():
        return None

@app.route('/catalog/JSON')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[category.serialize for category in categories])


# JSON API to show category info
@app.route('/catalog/<int:catalog_id>/JSON')
@app.route('/catalog/<int:catalog_id>/books/JSON')
def showCategoryJSON(catalog_id):
    books = session.query(Book).filter_by(category_id=catalog_id).all()
    return jsonify(books=[book.serialize for book in books])


# JSON API to show book info
@app.route('/catalog/<int:catalog_id>/books/<int:book_id>/JSON')
def showBookJSON(catalog_id, book_id):
    book = session.query(Book).filter_by(id=book_id).first()
    return jsonify(book=[book.serialize])


@app.route('/')
@app.route('/home')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    return render_template('catalogs.html', categories=categories)


@app.route('/catalog/<int:category_id>/books')
def showBooks(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Book).filter_by(category_id=category_id).order_by(
                                                        asc(Book.name))
    return render_template('items.html', items=items,
                           categories=categories, category=category)


@app.route('/catalog/<int:category_id>/books/<int:item_id>')
def showBookInfo(category_id, item_id):
    items = session.query(Book).filter_by(category_id=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Book).filter_by(id=item_id).one()
    return render_template('iteminfo.html', item=item,
                           items=items, category=category)


@app.route('/catalog/<int:category_id>/genre/new', methods=['GET', 'POST'])
def newBook(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newitem = Book(name=request.form['name'],
                       description=request.form['desc'],
                       category_id=category_id,
                       user_id=login_session['user_id'])
        session.add(newitem)
        session.commit()
        return redirect(url_for('showBooks', category_id=category_id))

    else:
        return render_template('newitem.html', category=category)


@app.route('/catalog/<int:category_id>/book/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editBook(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    book = session.query(Book).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            book.name = request.form['name']
        if request.form['desc']:
            book.description = request.form['desc']
        session.add(book)
        session.commit()
        return redirect(url_for('showBooks', category_id=category_id))

    else:
        return render_template('edititem.html', book=book)


@app.route('/catalog/<int:category_id>/book/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    book = session.query(Book).filter_by(id=item_id).one()

    # Get creator of book
    creator = getUserInfo(book.user_id)

    # Check if logged in user is creator of book
    if creator.id != login_session['user_id']:
        return redirect('/login')

    if request.method == 'POST':
        session.delete(book)
        session.commit()
        return redirect(url_for('showBooks', category_id=category_id))
    else:
        return render_template('deleteitem.html', book=book)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
