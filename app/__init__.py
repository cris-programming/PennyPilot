from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Definiamo il percorso del database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "app.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "imposta-una-chiave-segreta-molto-complessa"  # Cambia questa chiave!
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
