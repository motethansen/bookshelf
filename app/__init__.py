from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config.from_object('config')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
bootstrap = Bootstrap(app)

from app import views