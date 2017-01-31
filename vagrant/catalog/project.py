from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalogDB import Base, Categories, Items
#imported the Flask class
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
#An instance of this class is created which is our WSGI application.
app = Flask(__name__)

# This login_session object works like a dictionary
# we can store values in it for longevity of user's
# session with out server
from flask import session as login_session
import random, string

# import string
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///catalog_app.db')
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
	# state variable is 32 characters long and be a mix of uppercase and lower case and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # this is generate a unique state variable whenever we refresh the page
    # for cros-site request forgery, the attacker would essentially have to guess
    # this code in order to make a request on the user's behalf
    # later on, we will chec to make sure the user and the login session still
    # have the same state value when a user tries to authenticate
    return "The current session state is %s" % login_session['state']


#route() decorator to tell Flask what URL should trigger our function
@app.route('/')
def HelloWorld():
	return 'Hello,World!'
@app.route('/category/<int:category_id>/')
def HelloCatalog(category_id):
	category = session.query(Categories).filter_by(id=category_id)
	items = session.query(Items).filter_by(category_id = category_id)
	return render_template('menu.html',category=category[0], items=items)


@app.route('/category/<int:category_id>/item/JSON')
def categoriesItemJSON(category_id):
    category = session.query(Categories).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(
        category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])

# ADD JSON ENDPOINT HERE
@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def menuItemJSON(category_id, item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)

@app.route('/category/<int:category_id>/new/', methods=['GET','POST'])
def newItem(category_id):
	if request.method == 'POST':
		newItem = Items(name=request.form['name'],
			description=request.form['description'],
			category_id=category_id)
		session.add(newItem)
		session.commit()
		flash("new menu item created!")
		return redirect(url_for('HelloCatalog',category_id=category_id))
	else:
		return render_template('newItem.html', category_id=category_id)

@app.route('/category/<int:category_id>/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_id, item_id):
	editedItem = session.query(Items).filter_by(id = item_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		flash("The selected item is edited!")
		return redirect(url_for('HelloCatalog',category_id=category_id))
	else:
		return render_template('editItem.html', category_id=category_id,
			item_id = item_id,item = editedItem)
	# return "page to edit a menu item. Task 2 complete!"



@app.route('/category/<int:category_id>/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(category_id, item_id):
	deletedItem = session.query(Items).filter_by(id = item_id).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("The selected Item  is deleted!")
		return redirect(url_for('HelloCatalog',category_id=category_id))
	else:
		return render_template('deleteItem.html', category_id=category_id,
			item_id = item_id,item = deletedItem)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	# enables debug support and the server will reload itself on code changes,
	# and it will also provide you with a helpful debugger if things go wrong
	app.debug = True
	# This will immediately launch a local server and
	# start the server on http://localhost:5000/.
	app.run(host='0.0.0.0', port = 5000)