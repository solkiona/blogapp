from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

import os 
from flask_bcrypt import Bcrypt
app = Flask(__name__)

app.config['SECRET_KEY'] = 'aaf5b7df11409dc852cbba7991157ab1f2b2590fccfea7662c075b9042f71822'

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
  
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'



from flaskblog import routes

with app.app_context():
    db.create_all()




