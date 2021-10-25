# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, render_template, session, flash, redirect, url_for, jsonify

import datetime
import math

from web_app import app
import web_app.config as config
import web_app.discord_api as discord_api

@app.context_processor
def utility_processor():

    def debug_enabled():
        return app.debug == True

    def date_to_string(date):
        return datetime.datetime.fromisoformat(date).strftime("%m/%d/%Y %H:%M")

    def seconds_to_string(seconds):
        """Given an integer of seconds return a string of time passed

        @seconds: integer

        returns: string
        """

        if seconds < 60:
            return f"{seconds}s"

        minutes = seconds / 60
        if minutes < 60:
            return "%sm" % math.floor(minutes)

        hours = minutes / 60
        if hours < 24:
            return "%sh" % math.floor(hours)

        days = hours / 24
        return "%sd" % math.floor(days)

    def seconds_to_string_full(seconds):
        """Given an integer of seconds return a string of time passed

        @seconds: integer

        returns: string
        """

        if seconds < 60:
            return f"{seconds} " + ("second" if seconds == 1 else "seconds")

        minutes = seconds / 60
        if minutes < 60:
            return "%s " % math.floor(minutes) + ("minute" if minutes == 1 else "minutes")

        hours = minutes / 60
        if hours < 24:
            return "%s " % math.floor(hours) + ("hour" if hours == 1 else "hours")

        days = hours / 24
        return "%s " % math.floor(days) + ("day" if days == 1 else "days")

    def remaining_strike_time(created_date, seconds):
        """Given an iso formatted date and integer of seconds return a string of time remaining

        @created_date: string iso formatted date
        @seconds: integer

        returns: string
        """

        issued_date =  datetime.datetime.fromisoformat(created_date)
        expire_date = issued_date + datetime.timedelta(seconds=seconds)
        delta = expire_date - datetime.datetime.now()
        return seconds_to_string(delta.seconds)

    def build_avatar_url(user_id, avatar):
        """
        Builds the avatar url with the CDN and formats
        """
        return discord_api.get_avatar(user_id, avatar)

    return dict(debug_enabled=debug_enabled, date_to_string=date_to_string, seconds_to_string=seconds_to_string, seconds_to_string_full=seconds_to_string_full,
        build_avatar_url=build_avatar_url, remaining_strike_time=remaining_strike_time)

def rend_folder_template(folder, name, **kwargs):

    if 'mobile' in request.headers['User-Agent'].lower():
        return render_template('%s/%s.html' % (folder, name), **kwargs)

    else:
        return render_template('%s/%s.html' % (folder, name), **kwargs)

def verify_session(fn):
    def inner(*args,**kwargs):
        if not 'logged_in' in session:
            flash("You are not logged in.<br/>Please, log in to use our application.", "danger")
            return redirect(url_for('session.login'))
        
        return fn(*args,**kwargs)
    return inner

def verify_admin_session(fn):
    def inner(*args,**kwargs):
        if not 'logged_in' in session:
            flash("You are not logged in.<br/>Please, log in to use our application.", "warning")
            return redirect(url_for('session.login'))
        elif session["type"] != "admin":
            flash("Access denied.", "danger")
            return redirect(url_for('dashboard.index'))
        return fn(*args,**kwargs)
    return inner

def verify_not_session(fn):
    def inner(*args,**kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index.index'))
        return fn(*args,**kwargs)
    return inner

def verify_api_session(fn):
    def inner(*args,**kwargs):
        if 'd-api-key' not in request.headers or request.headers[config.API_SESSION_IDENTIFIER] != config.BOT_API_KEY:
            return jsonify({'error': True, 'message': 'Missing headers in request.'})
        return fn(*args,**kwargs)
    return inner

def seconds_to_string(seconds):
    """Given an integer of seconds return a string of time passed

    @seconds: integer

    returns: string
    """

    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds / 60
    if minutes < 60:
        return "%sm" % math.floor(minutes)

    hours = minutes / 60
    if hours < 24:
        return "%sh" % math.floor(hours)

    days = hours / 24
    return "%sd" % math.floor(days)