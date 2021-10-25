# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for, flash

import random
import string
import discord

from web_app.config import SERVER_ID, DISCORD_CLIENT_ID, DISCORD_REDIRECT_URL, ALLOWED_IDS
import web_app.discord_api as discord_api

import pprint


oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/oauth2', methods=['GET'], endpoint="redirect")
def oauth2_redirect():
    state = ''.join(random.choice(string.ascii_letters) for i in range(12))
    session['state'] = state

    redirect_url = 'https://discord.com/api/oauth2/authorize?client_id={0}&redirect_uri={1}&state={2}&response_type=code&scope=identify%20guilds'
    redirect_url = redirect_url.format(DISCORD_CLIENT_ID, DISCORD_REDIRECT_URL, state)

    return redirect(redirect_url)


@oauth_bp.route('/oauth2/authorize', methods=['GET'], endpoint="oauth_authorize")
def oauth2_followup_session():
    # Example response. http://localhost:11000/oauth2/authorize?code=CBonOcmMV3SXKbF99u5Ckq4jhhDeLY&state=NhfRKANjseJa
    # request.args = ImmutableMultiDict([('code', 'CBonOcmMV3SXKbF99u5Ckq4jhhDeLY'), ('state', 'NhfRKANjseJa')])

    if request.args.get('state') != session['state']:
        flash('The state returned by Discord Oauth2 is incorrect.', 'danger')
        return redirect(url_for('session.login'))

    if not request.args.get('code'):
        flash('The code returned by Discord Oauth2 is incorrect.', 'danger')
        return redirect(url_for('session.login'))

    auth = discord_api.get_auth_token(request.args['code'])

    if auth.get("error"):
        flash('There was an issue requesting an Access Token from Discord.', 'danger')
        return redirect(url_for('session.login'))

    user = discord_api.get_self(auth['access_token'])
    guilds = discord_api.get_guilds(auth['access_token'])

    if not user['id'] in ALLOWED_IDS:
        if SERVER_ID not in [guild['id'] for guild in guilds]:
            flash('You need to be part of Mooncord to access the website.', 'danger')
            return redirect(url_for('session.login'))

        for guild in guilds:
            if guild['id'] == SERVER_ID:
                perms = discord.permissions.Permissions(guild['permissions'])
                if not (perms.administrator or perms.kick_members):
                    flash("You need to be part of Mooncord's Moderation team to access the website.", 'danger')
                    return redirect(url_for('session.login'))

                session['permissions'] = guild['permissions']
                session['admin'] = perms.administrator
                session['mod'] = perms.kick_members

    session.clear()
    session['logged_in'] = True

    session['access_token'] = auth['access_token']
    session['expires_in'] = auth['expires_in']
    session['refresh_token'] = auth['expires_in']

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['discriminator'] = user['discriminator']
    session['avatar'] = user['avatar']

    return redirect(url_for('dashboard.index'))
