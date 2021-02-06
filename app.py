import os
from flask import Flask, render_template, url_for, redirect,request,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
