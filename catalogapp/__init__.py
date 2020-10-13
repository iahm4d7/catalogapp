from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from catalogapp.database_setup import Base
from flask_bcrypt import Bcrypt




# Connect to Database
engine = create_engine('sqlite:///books_catalog2.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
bcrypt = Bcrypt(app)


from catalogapp import routes
