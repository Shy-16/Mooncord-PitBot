# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for

from web_app.utils import rend_folder_template

index_bp = Blueprint('index', __name__)

@index_bp.route('/', endpoint="index")
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard.index'))

    return redirect(url_for('session.login'))
