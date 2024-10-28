from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_hashing import Hashing
from orderapp.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
hashing = Hashing(app)

# Import views after app initialization
from orderapp.views import staff, customer, main
