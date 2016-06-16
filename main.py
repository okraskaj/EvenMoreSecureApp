#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, make_response, redirect
from pymongo import MongoClient
import uuid
from pass_cor import hash_password, check_password, calculate_entropy

app = Flask(__name__)

client = MongoClient("mongodb://localhost")
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
@app.route('/<user>')
def index(user=None):
    return render_template("profile.html", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login(login=None):
    if request.method == "POST":
        login = request.form['login']
        passwd = request.form['passwd']
        resp = make_response(render_template('login.html', messg="Succesfully logged in!"))

        if is_login_in_db(login):
            real_password = users[login]['hashpasswd']
            if check_password(real_password, passwd):
                cookie = str(uuid.uuid4().hex)+":"+login
                users[login]['cookie'] = cookie
                resp.set_cookie('logged', cookie)
                return resp
            else:
                return render_template('login.html', error="Bad password or login")
        else:
            return render_template('login.html', error="Bad login or password")


    elif request.method == "GET":
        return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register(user=None):
    if request.method == "POST":
        login = request.form['login']
        passwd = request.form['passwd'].strip()
        if is_login_in_db(login):
            return render_template('register.html',
                                   error="This login is alredy taken")
        else:
            if len(passwd) < 5:
                return render_template('register.html',
                                       error="Password have to contain at least 5 characters")
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
                    return render_template('register.html',
                                           messg="You've registered succesfully. You can now log in.",
                                           registered="True" )

    elif request.method == "GET":
        return render_template("register.html")



@app.route('/posts')
def posts(user=None):
    posts_raw = db.posts.find()
    posts = []
    for document in posts_raw:
        new_post = {}
        new_post['title']=document['title']
        new_post['content']=document['content']
        new_post['author_login']=document['author']
        new_post['id']=document['_id']
        posts.append(new_post)

    return render_template('globalwall.html',posts = posts)



@app.route('/post/new', methods=['GET', 'POST'])
def postnew(user=None):
    cookie = request.cookies.get('logged')
    local_login = cookie.split(':')[1]

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

    elif request.method == "GET":
        posts_raw = db.posts.find()
        posts = []
        if cookie and users[local_login]['cookie'] == cookie:
            for document in posts_raw:
                new_post = {}
                new_post['title']=document['title']
                new_post['content']=document['content']
                new_post['author']=document['author']
                new_post['id']=document['_id']
                posts.append(new_post)

            return render_template('newpost.html',posts = posts)
        else:
            return redirect('/login',error="To add new posts you have to be logged in")


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
