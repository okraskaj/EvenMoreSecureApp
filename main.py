#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template, make_response, redirect,url_for
from pymongo import MongoClient
import uuid
from pass_cor import hash_password, check_password, calculate_entropy

app = Flask(__name__)

client = MongoClient(
#	os.environ['DB_PORT_27017_TCP_ADDR'],27017)
       '0.0.0.0:27017')
db = client.facebuk
usersdb = db.users
users = {}
cursor = db.users.find()
for document in cursor:
    temp_user = {}
    temp_user["id"] = document['_id']
    temp_user["login"] = document['login']
    temp_user["hashpasswd"] = document['hashpasswd']
    users[document['login']] = temp_user

def is_login_in_db(login):
    return db.users.find_one({'login': login})


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login(login=None, message=None):
    if request.method == "POST":
        login = request.form['login']
        passwd = request.form['passwd']

        if is_login_in_db(login):
            real_password = users[login]['hashpasswd']
            if check_password(real_password, passwd):
                cookie = str(uuid.uuid4().hex)+":"+login
                global users
                users[login]['cookie'] = cookie
                resp = make_response(render_template('login.html', user=login, message="Succesfully logged in!"))
                resp.set_cookie('logged', cookie)
                return resp
            else:
                return render_template('login.html', message="Bad password or login")
        else:
            return render_template('login.html', message="Bad login or password")
    elif request.method == "GET":
        if request.args:
            message = request.args['message']
        return render_template("login.html",message=message)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    resp = make_response(render_template('loggedout.html'))
    resp.set_cookie('logged', '', expires=0)
    return resp

@app.route('/register', methods=['GET', 'POST'])
def register(user=None):
    if request.method == "POST":
        login = request.form['login']
        passwd = request.form['passwd'].strip()
        passwdrp =request.form['passwd-rp'].strip()

        if is_login_in_db(login):
            return render_template('register.html',
                                   error="This login is alredy taken")
        else:
            if passwd != passwdrp:
                return render_template('register.html',
                                       error="Passwords have to be identical.")
            elif len(passwd) < 5:
                return render_template('register.html',
                                       error="Password have to contain at least 5 characters.")
            else:
                entropy = calculate_entropy(passwd)
                if entropy < 47:
                    return render_template('register.html',
                                           error="You have to create harder password. Consider using upper case letters and digits. %d" % entropy)
                else:
                    # now we know that everything is ok
                    new_user = {}
                    new_user['login'] = login
                    hash = hash_password(passwd)
                    new_user['hashpasswd'] = hash
                    _id = db.users.insert(
                        {
                            "login": login,
                            "hashpasswd": hash
                        }
                    )
                    new_user['id'] = _id
                    users[login] = new_user
                    return redirect('/login')
    elif request.method == "GET":
        return render_template("register.html")



@app.route('/posts')
def posts(user=None):
    if request.cookies.get('logged'):
        cookie = request.cookies.get('logged')
        user = cookie.split(':')[1]
        print users[user]
        posts_raw = db.posts.find()
        posts = []


        for document in posts_raw:
            new_post = {}
            new_post['title']=document['title']
            new_post['content']=document['content']
            new_post['autor']=document['author']
            new_post['id']=document['_id']
            posts.append(new_post)

        return render_template('globalwall.html',posts = posts, user= user)
    else:
        return redirect(url_for('login', message="You have to be logged in to view posts."))


@app.route('/myposts')
def myposts(user=None):
    if request.cookies.get('logged'):
        cookie = request.cookies.get('logged')
        user = cookie.split(':')[1]
        print users[user]
        posts_raw = db.posts.find()
        posts = []

        for document in posts_raw:
            new_post = {}
            new_post['title']=document['title']
            new_post['content']=document['content']
            new_post['autor']=document['author']
            new_post['id']=document['_id']
            posts.append(new_post)

        return render_template('myposts.html',posts = posts, user= user)
    else:
        return redirect(url_for('login', message="You have to be logged in to view posts."))


@app.route('/post/new', methods=['GET', 'POST'])
def postnew(user=None):
    if request.cookies.get('logged'):
        cookie = request.cookies.get('logged')
        local_login = cookie.split(':')[1]
        if cookie and users[local_login]['cookie'] == cookie:
            if request.method == "POST":
                if cookie and users[local_login]['cookie'] == cookie:
                    title = request.form['title']
                    content = request.form['content'].strip()
                    author = local_login
                    _id = db.posts.insert(
                        {
                            "title": title,
                            "content": content,
                            "author": author
                        }
                    )
                    return redirect('/posts')
                else:
                    return redirect('/login')

            elif request.method == "GET":
                return render_template('newpost.html', user=local_login)
        else:
            return redirect(url_for('login', message="You have to be logged in to add new post."))
    else:
         return redirect(url_for('login', message="You have to be logged in to add new post."))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000,debug="True")

