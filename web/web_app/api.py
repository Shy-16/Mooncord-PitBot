# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

import requests
import json

def do_login_call(endpoint, data=None, headers=None):

    if not data:
        data = dict()

    if not headers:
        headers = {"content-type": "application/x-www-form-urlencoded"}

    request = requests.post(endpoint, data=data, headers=headers)

    return request

def do_api_call(endpoint, auth_token, data=None, headers=None, method="GET"):

    if not data:
        data = dict()

    if not headers:
        headers = {
            'Authorization': 'Bearer %s' % auth_token,
            'content-type': 'application/json; charset=utf8'
        }

    if method == "GET":
        request = requests.get(endpoint, headers=headers, params=data)

    elif method == "POST":
        request = requests.post(endpoint, headers=headers, data=json.dumps(data))

    elif method == "PUT":
        request = requests.put(endpoint, headers=headers, data=json.dumps(data))

    elif method == "DELETE":
        request = requests.delete(endpoint, headers=headers, params=data)

    return request

def do_bot_call(endpoint, auth_token, data=None, headers=None, method="GET"):

    if not data:
        data = dict()

    if not headers:
        headers = {
            'Authorization': 'Bot %s' % auth_token,
            'content-type': 'application/json; charset=utf8'
        }

    if method == "GET":
        request = requests.get(endpoint, headers=headers, params=data)

    elif method == "POST":
        request = requests.post(endpoint, headers=headers, data=json.dumps(data))

    elif method == "PUT":
        request = requests.put(endpoint, headers=headers, data=json.dumps(data))

    elif method == "DELETE":
        request = requests.delete(endpoint, headers=headers, params=data)

    return request

def do_bot_call_upload(endpoint, auth_token, data=None, file=None, headers=None, method="POST"):

    if not data:
        data = dict()

    if not headers:
        headers = {
            'Authorization': 'Bot %s' % auth_token
        }

    if method == "POST":
        request = requests.post(endpoint, headers=headers, data=data, files={f"{file.filename}": (f"{file.filename}", file, f"{file.mimetype}")})

    elif method == "PUT":
        request = requests.put(endpoint, headers=headers, data=data, files={f"{file.filename}": (f"{file.filename}", file, f"{file.mimetype}")})

    return request