#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import uuid


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode('utf-8')).hexdigest() + ':' + salt

def check_password(hashed_password, given_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + given_password.encode('utf-8')).hexdigest()

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


