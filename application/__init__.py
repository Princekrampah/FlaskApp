from flask import Flask
from flask import url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

app = Flask(__name__, template_folder="templates", static_folder="static")

app.config["SECRET_KEY"] = '5753944b6b64e743b6b202336ea9cd25'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login to acess this page"
login_manager.login_message_category = "info"


from application import routes