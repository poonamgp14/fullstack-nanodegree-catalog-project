import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# There are three most important components in sqlalchemy code:
# DB table, mapper (maps a Python class to a DB table), class object (defines how a db record maps to a python object)
#Instead of writing code for all three components separately, sqlalchemy's declarative allows
# all three to be defined at once in one class definition

class Categories(Base):
	__tablename__ = 'categories'
	# Here we define columns for the table
	# Notice that each column is also a normal Python instance attribute.
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	description = Column(String(250),nullable=False)


class Items(Base):
	__tablename__ = 'items'
	# Here we define columns for the table
	# Notice that each column is also a normal Python instance attribute.
	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	description = Column(String(250),nullable=False)
	category_id = Column(Integer, ForeignKey('categories.id'))
	categories = relationship(Categories)


# We added this serialize function to be able to send JSON objects in a
# serializable format
	@property
	def serialize(self):
		return {
			'name': self.name,
			'description': self.description,
			'id': self.id
			# 'price': self.price,
			# 'course': self.course,
		}


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///catalog_app.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)