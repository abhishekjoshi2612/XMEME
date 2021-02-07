import os
from flask import Flask, render_template, url_for, redirect,request,flash,session
from urllib.request import urlopen
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    caption = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(120),  nullable=False)
    db.UniqueConstraint(name,caption,url)
    def __init__(self,name,caption,url):
        self.name = name
        self.caption = caption
        self.url = url
    def __repr__(self):
        return '<User %r>' % self.name

def is_url(url):
    try:
         response = requests.get(url)
         print("its done")
         return True
    except :
        print("OOPSIE")
        return False

def check_url(url):
    if is_url(url):
        image_formats = ("image/png","image/jpeg","image/jpg","image/gif")
        site = urlopen(url)
        meta = site.info()
        if meta["content-type"] in image_formats:
            print('og bro')
            return True
        else:
            print(meta["content-type"])
            return False
    else:
        return False

#db.create_all()


@app.route('/')
def hi():
    return render_template('home_page.html')
@app.route('/register',methods = ["POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        caption = request.form["caption"]
        url = request.form["url"]
        if check_url(url):
            data = User(name = name,caption = caption,url = url)
            users = User.query.filter_by(name=request.form["name"],caption = request.form["caption"],url = request.form["url"]).first()
            if users is None:
                db.session.add(data)
                db.session.commit()
                print("YOddddd")
               # flash('Your meme is submitted')
                return render_template('home_page.html',alert = 1)
            else:
               # flash('HEY THIS NAME ,CAPTION and URL already exists in our database')
               # error = 'HEY THIS NAME ,CAPTION and URL already exists in our database'
               print('copy cat')
               return render_template('home_page.html',alert = 2)
        else:
           # print("baddd")
           # flash('HEY YOUR URL DOES NOT CONTAIN AN VALID IMAGE THE IMAGE SHOULD BE IN PNG,JPG,JPEG OR IN GIF FORMAT')
           # error = 'HEY YOUR URL DOES NOT CONTAIN AN VALID IMAGE THE IMAGE SHOULD BE IN PNG,JPG,JPEG OR IN GIF FORMAT'
          #  return "HEY YO"
           print('hey invalid format')
           return render_template('home_page.html',alert = 3)






if __name__ == "__main__":
    app.run(debug=True) 
