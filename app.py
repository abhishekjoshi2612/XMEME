import os
from flask import Flask, render_template, url_for, redirect,request,flash,session,jsonify
from flask_api import status
from urllib.request import urlopen
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table
import requests
#import jsonify



app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['JSON_SORT_KEYS'] = False
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
        try:
            site = urlopen(url)
            meta = site.info()
            if meta["content-type"] in image_formats:
                print('og bro')
                return True
            else:
             print(meta["content-type"])
             return False
        except: 
            return False
    else:
        return False

#db.create_all()

Users = [ users for users in User.query.all()]
Users.reverse()
@app.route('/')
def hi():
    return render_template('home_page.html',userdetail = Users)
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
                return render_template('home_page.html',alert = 1,userdetail = Users)
            else:
               # flash('HEY THIS NAME ,CAPTION and URL already exists in our database')
               # error = 'HEY THIS NAME ,CAPTION and URL already exists in our database'
               print('copy cat')
               return render_template('home_page.html',alert = 2,userdetail = Users)
        else:
           # print("baddd")
           # flash('HEY YOUR URL DOES NOT CONTAIN AN VALID IMAGE THE IMAGE SHOULD BE IN PNG,JPG,JPEG OR IN GIF FORMAT')
           # error = 'HEY YOUR URL DOES NOT CONTAIN AN VALID IMAGE THE IMAGE SHOULD BE IN PNG,JPG,JPEG OR IN GIF FORMAT'
          #  return "HEY YO"
           print('hey invalid format')
           return render_template('home_page.html',alert = 3,userdetail = Users)



@app.route('/memes/<int:id>',methods = ['GET'])
def fetching(id):
    if request.method == "GET":
        if User.query.filter_by(id = id).first() is None:
            content = {'please move along':'your id is not here'}
            return content,status.HTTP_404_NOT_FOUND
        else:
         id_data = User.query.filter_by(id = id).first() 
         data_to_send =  { "id":id,  "name": id_data.name, "url":id_data.url,  "caption": id_data.caption}
         return jsonify(data_to_send),200
    else:
        return {'bad','request'},400


@app.route('/memes',methods = ['POST'])
def fetch_now():
    if request.method == "POST":
        request_json = request.get_json(force = True)
        url = request_json.get("url")
        name = request_json.get("name")
        caption = request_json.get("caption")
        
        bad_request = {"invalid":"request"}
        print(name," ",caption," ",url)
        if name is None:
            print('name wrong')
            return bad_request,400
        if url is None or check_url(url) is False:
            print('url wrong')
            return bad_request,400
        if caption is None:
            print('caption wrong')
            return bad_request,400
        
        the_id = User.query.filter_by(url = url,name = name,caption = caption).first()
        if the_id is None:
            data = User(name = name,caption = caption,url = url)
            db.session.add(data)
            db.session.commit()
            id_data = {"id":User.query.filter_by(url = url,name = name,caption = caption).first().id}
            return jsonify(id_data),400
        else:
            print('hdhd')
            return jsonify(bad_request),400
    else:
        return jsonify(bad_request),400
        






if __name__ == "__main__":
    app.run(debug=True) 
