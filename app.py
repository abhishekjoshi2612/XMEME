import os
from flask import Flask, render_template, url_for, redirect,request,flash,session,jsonify
from flask_api import status
from urllib.request import urlopen
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table
import requests



app = Flask(__name__)
#app.config['SECRET_KEY'] = 'mysecret'
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

@app.route('/swagger-ui')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')

@app.route('/editit')
def hello():
    return render_template('edit.html')
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





@app.route('/edit',methods=["POST"])
def edit():
    if request.method == "POST":
        id = request.form["id"]
        caption = request.form["caption"]
        url = request.form["url"]
        if check_url(url) and url is not None and caption is not None and id is not None:
            users = User.query.filter_by(id=request.form["id"]).first()
            if users is None:
                return render_template('edit.html',msg = 2),404
            else:
                user = User(name = users.name,caption = users.caption,url = users.url)
                db.session.add(user)
                db.session.commit()
                return render_template('edit.html',msg = 1)
        else:
            return  render_template('edit.html',msg = 2),404




@app.route('/memes/<int:id>',methods = ["GET","PATCH"])
def fetch_id(id):
    if request.method == "GET":
        if User.query.filter_by(id = id).first() is None:
            
            return ('',404)
        else:
            user =  User.query.filter_by(id = id).first()
            user_detail = jsonify({"id":user.id,"name":user.name,"url":user.url,"caption":user.caption})
            print(user_detail)
            user_detail.headers.add('Access-Control-Allow-Origin','*')
            user_detail.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
            return user_detail,200
    if request.method == "PATCH":
        if User.query.filter_by(id = id).first() is None:
            
            return ('',404)
        else:
            request_json = request.get_json(force = True)
            url = request_json.get("url")
            name = request_json.get("name")
            caption = request_json.get("caption")
            if name is None:
                print("yo")
                user =  User.query.filter_by(id = id).first()
                user.caption = caption
                user.url = url
                db.session.commit()
                response = jsonify({"200":"200"})
                response.headers.add('Access-Control-Allow-Origin','*')
                response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
                return(response,200)
            else:
                print("wut")
                return ('',400)
                



@app.route('/memes',methods = ["GET","POST"])
def fetch_now():
    if request.method == "GET" :  
        print('yo')
        count = 0
        Users_count = []
        for user in Users:
            count += 1
            Users_count.append({"id":user.id,"name":user.name,"url":user.url,"caption":user.caption})
            if count == 100:
                break
        Users_count.reverse()
        
        return jsonify(Users_count),200

    if request.method == "POST":
        request_json = request.get_json(force = True)
        print(request_json)
        url = request_json.get("url")
        name = request_json.get("name")
        caption = request_json.get("caption")
        
        bad_request = {"invalid":"request"}
        print(name," ",caption," ",url)
        if name is None:
            print('name wrong')
            return ('',400)
        if url is None or check_url(url) is False:
            print('url wrong')
            return ('',400)
        if caption is None:
            print('caption wrong')
            return ('',400)
        
        the_id = User.query.filter_by(url = url,name = name,caption = caption).first()
        if the_id is None:
            data = User(name = name,caption = caption,url = url)
            db.session.add(data)
            db.session.commit()
            id_data = {"id":User.query.filter_by(url = url,name = name,caption = caption).first().id}
            return jsonify(id_data),200
        else:
            print('hdhd')
            return ('',409)


        





        






if __name__ == "__main__":
     app.run(threaded = True)
