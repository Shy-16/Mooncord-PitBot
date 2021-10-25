# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for, flash, jsonify

import datetime
import json
import bson
from bson.objectid import ObjectId

from web_app.config import SERVER_ID
from web_app.utils import rend_folder_template, verify_session
from web_app.database import Database

banwords_bp = Blueprint('banwords', __name__)

@banwords_bp.route('/banwords', methods=['GET'], endpoint="index")
@verify_session
def index():
    db = Database()

    banwords = db.get_banwords(SERVER_ID)

    return rend_folder_template('banwords', 'index', banwords=banwords)

@banwords_bp.route('/banwords', methods=['POST'], endpoint="create")
@verify_session
def create_banword():
    db = Database()

    data = request.json

    banword = db.add_banword(SERVER_ID, data)
    banword['_id'] = str(banword['_id'])
    banword['guild_id'] = str(banword['guild_id'])
    banword['user_id'] = str(banword['user_id'])

    return jsonify(banword), 201

@banwords_bp.route('/banwords/<banword_id>', methods=['GET'], endpoint="get")
@verify_session
def get_banword(banword_id):

    db = Database()
    banword = db.get_banword(banword_id)
    banword['_id'] = str(banword['_id'])
    banword['guild_id'] = str(banword['guild_id'])
    banword['user_id'] = str(banword['user_id'])

    return jsonify(banword), 200