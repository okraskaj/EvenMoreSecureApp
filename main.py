#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)
users = {"Jan","Adam","Ewa","Marcin", "Paweł", "Kasia", "Bartek"}


@app.route('/')
def index():
    return 'This is the homepage'

@app.route('/users')
def list_users():
    return 'List of all users'

@app.route('/profile/<username>')
def profile(username):
    if username in users:
        return 'This is the %s\'s wall' % username
    else:
        return 'This user is not created yet'
if __name__ == '__main__':
    app.run(debug=True)
