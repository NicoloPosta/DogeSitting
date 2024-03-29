from logging import error
from flask import Flask, json, render_template, redirect, url_for, jsonify, request
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
from os import path
app = Flask(__name__)
current_dir = path.dirname(path.realpath(__file__))
app.config['SECRET_KEY'] = 'WhenInDoubtWhipItOut'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db.create_all()
from route import *

if __name__ == '__main__':
    app.run(debug=True)
