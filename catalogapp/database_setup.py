import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from catalogapp import login_manager
from flask_login import UserMixin


Base = declarative_base()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""User class """
class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(60),nullable=False)
    image_file = Column(String(20), nullable=False, default='default.jpg')

"""Category class """


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return object data in serializeable format
        return {
            'id': self.id,
            'name': self.name,
        }
"""Book class """


class Book(Base):
    __tablename__ = 'book'

    name = Column(String(80), nullable=False)
    description = Column(String(250))
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return object data in serializeable format"""
        return {
            'category': self.category.name,
            'description': self.description,
            'name': self.name,
        }

# engine = create_engine('sqlite:///books_catalog.db')
engine = create_engine('sqlite:///books_catalog2.db')
Base.metadata.create_all(engine)
