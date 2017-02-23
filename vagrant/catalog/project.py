from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from catalogDB import Base, Category, Item, User
from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask import session as login_session
import random
import string
# IMPORTS FOR writing callback function which is called upon
# successful authorization from google server
# flow_from_clientsecrets creates a flow object from
# clientsecrets JSON file and stores your client ID, client sceret
# and other parameters
# FlowExchangeError method is used if we run into an error trying
# to exchange an authorzation code for an access token
# login_session object works like a dictionary
# we can store values in it for longevity of user's
# session with out server


# An instance of this class is created which is our WSGI application.
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


# import string
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
# engine = create_engine('sqlite:///catalog_app.db')
# engine = create_engine('sqlite:///groceryCatalog3.db')
engine = create_engine('sqlite:///catalog.db')
# engine = create_engine('sqlite:///catalog_appWithUsers2.db')
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
        # state variable is 32 characters long and be a mix of uppercase and
        # lower case and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # this is generate a unique state variable whenever we refresh the page
    # for cros-site request forgery, the attacker would essentially
    # have to guess
    # this code in order to make a request on the user's behalf
    # later on, we will chec to make sure the user and the login session
     # still
    # have the same state value when a user tries to authenticate
    # return "The current session state is %s" % login_session['state']
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    # confirm that token that client sends to the server
    # matches the token that server sent to the client
    # this ensure that the user is making the request and
    # not the malicious script
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.')
            , 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization/one-time code from my server
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        # try and exchange this one-time code for credentials object
        # which will contain the access token for my server
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    # login_session['credentials'] = credentials.access_token
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        # Store the access token in the session for later use.
        del login_session['access_token']
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id
        response = make_response(json.dumps(
            'Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # login_session['credentials'] = credentials.access_token
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'], 'login')
    print "done!"
    return output


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
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
# disconnect by telling the server to reject its access token


@app.route('/logout')
def gdisconnect():
    print(login_session)
    access_token = login_session.get('access_token')
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %
            login_session.get('access_token')
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        access_token = login_session.get('access_token')
        del access_token
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You have successfully logged out!", "logout")
        return redirect(url_for('showCategories'))
    else:
        # flash("You were not logged in!","logout")
        # return redirect(url_for('showCategories'))
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# ADD JSON ENDPOINT HERE


@app.route('/category/<int:category_id>/item/JSON')
def categoriesItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


# @app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
# def menuItemJSON(category_id, item_id):
#     item = session.query(Item).filter_by(id=item_id).one()
#     return jsonify(Item=item.serialize)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            # redirect('/login')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# route() decorator to tell Flask what URL should trigger our function


@app.route('/')
def HelloWorld():
    return render_template('home.html')


@app.route('/category/<int:category_id>/')
def showACategory(category_id):
    category = session.query(Category).filter_by(id=category_id)
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template('item.html', category=category[0], items=items)


# Show all restaurants
# @app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.id)).all()
    items = session.query(Item).group_by(
        Item.category_id).order_by(desc(Item.created_date)).all()
    print(categories)
    categoriesArr = []
    for category in categories:
        # print(category.id)
        categoriesObj = {}
        categoriesObj['name'] = category.name
        categoriesObj['id'] = category.id
        for item in items:
            if item.category_id == category.id:
                categoriesObj['item'] = item
                categoriesArr.append(categoriesObj)
                # print(category.item.name)
                break
        if 'item' in categoriesObj:
            pass
        else:
            categoriesObj['item'] = {'name': 'None'}
            categoriesArr.append(categoriesObj)

    # print(categoriesArr)
    if 'username' not in login_session:
        return render_template('publiccategories.html', categories=categoriesArr)
    else:
        return render_template('categories.html', categories=categoriesArr)

# Create a new category


@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], description=request.form['description'],
            user_id=login_session.get('user_id')
        )
        session.add(newCategory)
        flash('New Category %s Successfully Created' %
              newCategory.name, 'newCategory')
        session.commit()
        # categories = session.query(Category).order_by(asc(Category.id)).all()
        # print(categories)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/category/<int:category_id>/new/',
            methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    newItemInCate = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] == newItemInCate.user_id:
        if request.method == 'POST':
            print("I am here!")
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_id=category_id,
                           user_id=login_session.get('user_id')
                           )
            print(newItem)
            session.add(newItem)
            session.commit()
            flash("new item created!", 'newItem')
            return redirect(url_for('showACategory', category_id=category_id))
        else:
            return render_template('newItem.html', category_id=category_id)
    else:
        flash(
            "You are not authorized to add an item in the selected category!", 'notAuthorized')
        return redirect(url_for('showACategory', category_id=category_id))


@app.route('/category/<int:category_id>/<int:item_id>/edit/',
            methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] == editedItem.user_id:
        if request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
                editedItem.description = request.form['description']
                session.add(editedItem)
                session.commit()
                flash("The selected item is edited!", "editItem")
                return redirect(url_for('showACategory', category_id=category_id))
            if not request.form['name']:
                return redirect(url_for('showACategory', category_id=category_id))
        else:
            return render_template('editItem.html', category_id=category_id,
                                   item_id=item_id, item=editedItem)
    else:
        flash(
            "You are not authorized to edit the selected item!", 'notAuthorized')
        return redirect(url_for('showACategory', category_id=category_id))


@app.route('/category/<int:category_id>/<int:item_id>/delete/',
            methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
    deletedItem = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] == deletedItem.user_id:
        if request.method == 'POST':
            session.delete(deletedItem)
            session.commit()
            flash("The selected Item  is deleted!", "deleteItem")
            return redirect(url_for('showACategory', category_id=category_id))
        else:
            return render_template('deleteItem.html', category_id=category_id,
                                   item_id=item_id, item=deletedItem)
    else:
        flash(
            "You are not authorized to delete the selected item!",
            'notAuthorized')
        return redirect(url_for('showACategory', category_id=category_id))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    # enables debug support and the server will reload itself on code changes,
    # and it will also provide you with a helpful debugger if things go wrong
    app.debug = True
    # This will immediately launch a local server and
    # start the server on http://localhost:5000/.
    app.run(host='0.0.0.0', port=5080)
