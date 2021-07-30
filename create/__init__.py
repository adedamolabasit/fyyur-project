from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nautilus5he!@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='1378de085a8b2c078dfb4c4f'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from create import app
