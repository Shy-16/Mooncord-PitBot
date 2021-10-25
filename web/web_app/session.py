# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for

from web_app.utils import rend_folder_template, verify_session

session_bp = Blueprint('session', __name__)

@session_bp.route('/login', methods=['GET'], endpoint='login')
def get_login():

    if 'logged_in' in session:
        return redirect(url_for('dashboard_path'))

    return rend_folder_template('session', 'login')

@session_bp.route('/login', methods=['POST'], endpoint='post_login')
def post_login():
	
    pass

@session_bp.route('/logout', methods=['GET'], endpoint='logout')
def get_logout():
    session.clear()
    return redirect(url_for('index.index'))