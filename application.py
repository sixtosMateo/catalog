from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# connect to database & create database session
engine = create_engine('sqlite:///catalogitems.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def show_catalog():
    # all category objects stored
    categorys = session.query(Category).all()
    # all items onjects stored
    if 'username' in login_session:
        items = session.query(Item).filter_by(user_id=getUserID(
                              login_session['email'])).limit(7).all()
    else:
        items = session.query(Item).filter_by().limit(7).all()

    # renders template with categorys and items onjects
    return render_template('catalog.html', categorys=categorys, items=items)


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


# method creates user when its called with a session as parameter given
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# method returns user's object based on user_id as parameter given
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# method returns user's id based on email as parameter given
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:

        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current' +
                                            ' user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    # data is the response information that is given from google api
    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if the user exists, if it doesnt make a new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # get access token from session
    access_token = login_session.get('access_token')

    # if none 401 error message
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    # get result of url with access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url %= login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    # disconnect if successful
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('show_catalog'))
    else:
        response = make_response(json.dumps('Failed to revoke token for' +
                                 'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/<int:category_id>')
# method renders the catolog_item.html based on category id
def show_category_item(category_id):
    categorys = session.query(Category).all()
    if 'username' in login_session:
        items = session.query(Item).filter_by(
                              category_id=category_id, user_id=getUserID(
                                login_session['email'])).all()
    else:
        items = session.query(Item).filter_by(category_id=category_id).all()

    return render_template('catalog_item.html', items=items,
                           categorys=categorys)


@app.route('/<int:category_id>/<int:item_id>/')
# method renders the item_description.html based on the category id & item id
def show_item_description(category_id, item_id):
    items = session.query(Item).filter_by(id=item_id).one()
    categorys = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return render_template('public_item_description.html', items=items,
                               categorys=categorys)
    return render_template('item_description.html', items=items,
                           categorys=categorys)


@app.route('/addItem', methods=['GET', 'POST'])
# method renders addItem.html if user is logged in
# if form is posted will redirect to catalog.html
# else will redirect to login page
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
    categorys = session.query(Category).all()
    if request.method == "POST":
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       user_id=getUserID(login_session['email']))
        session.add(newItem)
        session.commit()
        return redirect(url_for('show_catalog'))

    return render_template('addItem.html', categorys=categorys)


@app.route('/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
# method renders deleteItem.html if user is logged in
# if form is posted will redirect to catalog.html
# else will redirect to login page
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    item = session.query(Item).filter_by(id=item_id).one()
    # checks for items.users_id with login_session['user_id'] to validate
    # authorization
    if item.user_id != login_session['user_id']:
        return "<script> function myFunction(){'youre not authorize to delete."
        + "Please create a restaurant in order to delete.';}</script>"
        + "<body onload=''myFunction()''>"

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('show_catalog'))
    return render_template('deleteItem.html', items=item)


@app.route('/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
# method renders editItem.html if user is logged in
# if form is posted will redirect to catalog.html
# else will redirect to login page
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    categorys = session.query(Category).all()
    items = session.query(Item).filter_by(id=item_id).one()

    # checks for items.users_id with login_session['user_id'] to validate
    # authorization
    if items.user_id != login_session['user_id']:
        return "<script> function myFunction(){'youre not authorize to edit."
        + "Please create a restaurant in order to edit.';}</script>"
        + "<body onload=''myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            items.name = request.form['name']
        if request.form['description']:
            items.description = request.form['description']
        if request.form['category']:
            items.category_id = request.form['category']
        session.add(items)
        session.commit()
        return redirect(url_for('show_catalog'))

    return render_template("editItem.html", items=items, categorys=categorys)


@app.route('/<int:category_id>/JSON')
# method will display items info based on category_id as JSON endpoint
def category_JSON(category_id):
    categorys = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[item.serialize for item in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
