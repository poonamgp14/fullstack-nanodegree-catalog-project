from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalogDB import Base, Category, Item, User

# engine = create_engine('sqlite:///catalog_app.db')
# engine = create_engine('sqlite:///catalog_appWithUsers2.db')
engine = create_engine('sqlite:///groceryCatalog3.db')
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

# Create dummy user
User1 = User(name="Govind Chaudhary", email="govindchaudhary@gmail.com",
             picture='')
session.add(User1)
session.commit()

# Insert a Categories in the person table
Biyearly = Category(name='Bi-yearly', user=User1)
session.add(Biyearly)
session.commit()


# Insert items in the Item table
item1 = Item(name='Kitchen Paper Towels',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=Biyearly,
             user=User1)
session.add(item1)
session.commit()

item2 = Item(name='Toilet Paper Towels',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=Biyearly,
             user=User1)
session.add(item2)
session.commit()

item3 = Item(name='Toileteries',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=Biyearly,
             user=User1)
session.add(item3)
session.commit()

# Insert a category in the Category table
quarterly = Category(name='Quarterly', user=User1)
session.add(quarterly)
session.commit()

# Insert items in the Item table
item4 = Item(name='Tooth Paste',
             description="Lorem ipsum dolor sit amet, consectetu",
             category=quarterly,
             user=User1)
session.add(item4)
session.commit()

item5 = Item(name='A Bottle of Olives',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=quarterly,
             user=User1)
session.add(item5)
session.commit()

item6 = Item(name='A Pack of Hemp Seeds',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=quarterly,
             user=User1)
session.add(item6)
session.commit()

# Insert a category in the Category table
weekly = Category(name='Weekly', user=User1)
session.add(weekly)
session.commit()

# Insert items in the Item table
item7 = Item(name='Besan Flour',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=weekly,
             user=User1)
session.add(item7)
session.commit()

item8 = Item(name='Carrot',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=weekly,
             user=User1)
session.add(item8)
session.commit()

item9 = Item(name='Pasta Spagetti',
             description="Lorem ipsum dolor sit amet, consectetur",
             category=weekly,
             user=User1)
session.add(item9)
session.commit()

# Insert a category in the Category table
biweekly = Category(name='Bi-weekly', user=User1)
session.add(biweekly)
session.commit()

# Insert items in the Item table
item10 = Item(name='Cottage Cheese',
              description="Lorem ipsum dolor sit amet, consectetur",
              category=biweekly,
              user=User1)
session.add(item10)
session.commit()

item11 = Item(name='Tofu',
              description="Lorem ipsum dolor sit amet, consectetur",
              category=biweekly,
              user=User1)
session.add(item11)
session.commit()

item12 = Item(name='Avacados',
              description="Lorem ipsum dolor sit amet, consectetur",
              category=biweekly,
              user=User1)
session.add(item12)
session.commit()
