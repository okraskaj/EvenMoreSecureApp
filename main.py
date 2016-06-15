#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,request,render_template, make_response
from pymongo import MongoClient
import hashlib
import uuid

app = Flask(__name__)



client = MongoClient("mongodb://localhost")
db = client.facebuk
usersdb = db.users
users = {}
cursor = db.users.find()
for document in cursor:

    #passwdhash = document['passwdhash']
    temp_user ={}
    temp_user["id"]=document['_id']
    temp_user["login"]=document['login']
    temp_user["hashpasswd"] = document['hashpasswd']
    temp_user["name"] = document['name']
    temp_user["height"] = document['height']
    temp_user["age"] = document['age']
    users[document['login']]=temp_user

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, given_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + given_password.encode()).hexdigest()

def calculate_entropy(password=''):
    import re
    from math import log, pow
    numeric = re.compile('\d')
    loweralpha = re.compile('[a-z]')
    upperalpha = re.compile('[A-Z]')
    symbols = re.compile('[-_.:,;<>?"#$%&/()!@~]')
    polish = re.compile('[ąęźćśóżńĄĘŻŹŚĆŃÓ]')
    num_of_symbols = 20
    charset = 0
    if numeric.search(password):
        charset += 10
    if loweralpha.search(password):
        charset += 26
    if upperalpha.search(password):
        charset += 26
    if polish.search(password):
        charset += 16
    if symbols.search(password):
        charset += num_of_symbols

    entropy = log(pow(charset, len(password)), 2)
    return entropy




@app.route('/')
@app.route('/<user>')
def index(user=None):
    return render_template("profile.html", user=user)


@app.route('/login',methods=['GET','POST'])
def login(login=None):
    if request.method == "POST":
        login = request.form['login']
        passwd = request.form['passwd']
        resp = make_response(render_template('login.html', messg="Succesfully logged in!"))

        if login in users.keys():
            real_password = users[login]['hashpasswd']
            if check_password(real_password, passwd):
                cookie = uuid.uuid4().hex
                resp.set_cookie('logged',cookie)
                users[login]['cookie']= cookie
                return resp
            else:
                return render_template('login.html', error="Bad password")

        else:
            return render_template('login.html', error="Bad login")


    elif request.method == "GET":
        return render_template("login.html")


@app.route('/register',methods=['GET','POST'])
def register(user=None):
    if request.method == "POST":
        login = request.form['login']
        passwd = request.form['passwd']
        passwdrep = request.form['passwdrep']
        if login in users:
            return render_template('register.html',error="This login is alredy taken")
        else:
            if passwdrep == passwd:
                if len(passwd)<5:
                    return render_template('register.html',error="Password have to contain at least 5 characters")
                else:
                    entropy = calculate_entropy(passwd)
                    if entropy<47:
                        return render_template('register.html', error="You have to create harder password. Consider using upper case letters and digits. %d" % entropy)
                    else:
                        #now we know that everything is ok
                        new_user = {}
                        new_user['login']= login
                        new_user['hashpasswd']= hash_password(passwd)
                        users[login]=new_user
                        return render_template('login.html',messg="You've registered succesfully. You can now log in.")



    elif request.method == "GET":
        return render_template("register.html")


@app.route('/posttest',methods=['GET','POST'])
def posttest():
    if request.method == "POST":
        return "POST HAS BEEN USED"
    else:
        return 'Method used: %s' % request.method

@app.route('/profile/<login>')
def profile(login):
    if login in users:
        return render_template("profile.html",user=users[login])

@app.route('/userslist')
def users_list():
    return render_template("users.html", users=users)

#
# @app.route('/profile/<username>/post/<int::post_id>')
# def posts(username,post_id):
#         if username in users:
#             user = users[username]
#             if post_id in user.posts
#             return 'This is the %s post numer %i' % username % post_id
#         else:
#             return 'This user is not created yet'




if __name__ == '__main__':
    app.run(debug=True)
