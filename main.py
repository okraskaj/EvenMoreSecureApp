#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,request,render_template

app = Flask(__name__)
users = {"Jan","Adam","Ewa","Marcin", "Paweł", "Kasia", "Bartek"}


@app.route('/')
def index():
    return 'Method used: %s' % request.method

@app.route('/posttest',methods=['GET','POST'])
def posttest():
    if request.method == "POST":
        return "POST HAS BEEN USED"
    else:
        return 'Method used: %s' % request.method


@app.route('/users')
def list_users():
    return 'List of all users'

@app.route('/profile/<name>')
def profile(name):
    if name in users:
        return render_template("profile.html",name=name)



#
# @app.route('/profile/<username>/post/<int::post_id>')
# def posts(username,post_id):
#         if username in users:
#             user = users[username]
#             #if post_id in user.posts
#             return 'This is the %s post numer %i' % username % post_id
#         else:
#             return 'This user is not created yet'
if __name__ == '__main__':
    app.run(debug=True)
