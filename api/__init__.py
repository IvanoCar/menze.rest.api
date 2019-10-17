from flask import Flask
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config.from_object("api.modules.utils.config.DevolopmentConfig")

db = PyMongo(app)

from api.modules.utils.auth import Auth

authentication = Auth()


from api.modules.restaurants.routes import restaurants_mod
from api.modules.users.routes import users_mod
from api.modules.healthcheck.routes import hcheck_mod


app.register_blueprint(restaurants_mod)
app.register_blueprint(users_mod)
app.register_blueprint(hcheck_mod)
