from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalogDB import Base, Categories, Items

engine = create_engine('sqlite:///catalog_app.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Insert a Categories in the person table
new_category = Categories(name='random1', description='I donot know')
session.add(new_category)
session.commit()

# Insert an Address in the address table
new_item = Items(name='random item1', description='this is again some random item',categories=new_category)
session.add(new_item)
session.commit()

# Insert a Categories in the person table
new_category2 = Categories(name='random2', description='I donot know again!')
session.add(new_category2)
session.commit()

# Insert an Address in the address table
new_item2 = Items(name='random item2', description='this is again some random item again!',categories=new_category2)
session.add(new_item2)
session.commit()