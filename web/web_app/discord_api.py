# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

import json

from web_app.api import do_login_call, do_api_call, do_bot_call, do_bot_call_upload
from web_app.config import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_API_URI, DISCORD_REDIRECT_URL, DISCORD_BOT_TOKEN, DISCORD_IMAGE_CDN

OAUTH2_TOKEN_ENDPOINT = '/oauth2/token'

USERS_ME_ENDPOINT = '/users/@me'
USERS_ENDPOINT = '/users/%s'
GET_GUILD_MEMBER_ENDPOINT = '/guilds/%s/members/%s' # guild_id, user_id
CREATE_CHANNEL_ENDPOINT = '/guilds/%s/channels' # guild_id
CREATE_MESSAGE_ENDPOINT = '/channels/%s/messages'
CREATE_THREAD_ENDPOINT = '/channels/%s/messages/%s/threads' # channel_id, message_id
GUILDS_ME_ENDPOINT = '/users/@me/guilds'
GUILDS_ENDPOINT = '/guilds/%s'

THREE_DAY_THREAD_ARCHIVE = 'THREE_DAY_THREAD_ARCHIVE'

def get_auth_token(code):
    """
    Does a login query to Discord and returns auth code

    returns {
      "access_token": "6qrZcUqja7812RVdnEKjpzOL4CvHBFG",
      "token_type": "Bearer",
      "expires_in": 604800,
      "refresh_token": "D43f5y0ahjqew82jZ4NViEr2YafMKhue",
      "scope": "identify"
    }
    """

    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URL
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = do_login_call(DISCORD_API_URI + OAUTH2_TOKEN_ENDPOINT, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def refresh_token(refresh_token):
    """
    Refreshes the token for a user.
    Returns same information as get_auth_token
    """

    data = {
        'client_id': config.DISCORD_CLIENT_ID,
        'client_secret': config.DISCORD_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
        #'redirect_uri': DISCORD_REDIRECT_URI,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = do_login_call(config.DISCORD_API_URI + OAUTH2_TOKEN_ENDPOINT, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_self(auth_token):
    """
    Gets auth token.
    Returns /users/@me
    {
      "id": "80351110224678912",
      "username": "Nelly",
      "discriminator": "1337",
      "avatar": "8342729096ea3675442027381ff50dfe",
      "verified": true,
      "email": "nelly@discord.com",
      "flags": 64,
      "premium_type": 1,
      "public_flags": 64
    }
    """

    response = do_api_call(DISCORD_API_URI + USERS_ME_ENDPOINT, auth_token)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_guilds(auth_token):
    """
    Gets user guilds.
    
    Returns /users/@me/guilds
    {
      "id": "80351110224678912",
      "name": "1337 Krew",
      "icon": "8342729096ea3675442027381ff50dfe",
      "owner": true,
      "permissions": "36953089",
      "features": ["COMMUNITY", "NEWS"]
    }
    """

    response = do_api_call(DISCORD_API_URI + GUILDS_ME_ENDPOINT, auth_token)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_bot_guilds():
    """
    Gets bot guilds.
    
    Returns /users/@me/guilds
    {
      "id": "80351110224678912",
      "name": "1337 Krew",
      "icon": "8342729096ea3675442027381ff50dfe",
      "owner": true,
      "permissions": "36953089",
      "features": ["COMMUNITY", "NEWS"]
    }
    """

    response = do_bot_call(DISCORD_API_URI + GUILDS_ME_ENDPOINT, DISCORD_BOT_TOKEN)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_user(user_id):
    """
    Gets user.
    Returns /users/user_id
    {
      "id": "80351110224678912",
      "username": "Nelly",
      "discriminator": "1337",
      "avatar": "8342729096ea3675442027381ff50dfe",
      "verified": true,
      "email": "nelly@discord.com",
      "flags": 64,
      "premium_type": 1,
      "public_flags": 64
    }
    """

    response = do_bot_call(DISCORD_API_URI + USERS_ENDPOINT % user_id, DISCORD_BOT_TOKEN)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_guild(guild_id):
    """
    Gets user.
    Returns /guilds/guild_id
    {
      "id": "2909267986263572999",
      "name": "Mason's Test Server",
      "icon": "389030ec9db118cb5b85a732333b7c98",
      "description": null,
      ...
    }

    https://discord.com/developers/docs/resources/guild#get-guild
    """

    response = do_bot_call(DISCORD_API_URI + GUILDS_ENDPOINT % guild_id, DISCORD_BOT_TOKEN)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_guild_member(guild_id, user_id):
    """
    Gets user.
    Returns /guilds/guild_id/members/user_id
    {
      "id": "80351110224678912",
      "username": "Nelly",
      "discriminator": "1337",
      "avatar": "8342729096ea3675442027381ff50dfe",
      "verified": true,
      "email": "nelly@discord.com",
      "flags": 64,
      "premium_type": 1,
      "public_flags": 64
      ...
    }

    https://discord.com/developers/docs/resources/guild#guild-member-object
    """

    response = do_bot_call(DISCORD_API_URI + GET_GUILD_MEMBER_ENDPOINT % (guild_id, user_id), DISCORD_BOT_TOKEN)
    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def send_message(channel_id, message):
    """
    Send a new message
    Returns a message object:
    https://discord.com/developers/docs/resources/channel#message-object
    """

    data = {'content': message}

    response = do_bot_call(DISCORD_API_URI + CREATE_MESSAGE_ENDPOINT % channel_id, DISCORD_BOT_TOKEN, data=data, method="POST")

    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def send_embed_message(channel_id, user, embeds=list()):
    """
    Send a new message with embeds
    Returns a message object:
    https://discord.com/developers/docs/resources/channel#message-object
    """

    data = {
        'embeds': embeds,
        'author': {
            'name': f"{user['username']}#{user['username_handle']}",
            'icon_url': get_avatar(user['discord_id'], user['avatar'])
        }
    }

    response = do_bot_call(DISCORD_API_URI + CREATE_MESSAGE_ENDPOINT % channel_id, DISCORD_BOT_TOKEN, data=data, method="POST")

    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def send_attachment(channel_id, att):
    """
    Send a new message
    Returns a message object:
    https://discord.com/developers/docs/resources/channel#message-object
    """

    data = {}

    response = do_bot_call_upload(DISCORD_API_URI + CREATE_MESSAGE_ENDPOINT % channel_id, DISCORD_BOT_TOKEN, data=data, file=att, method="POST")

    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def send_user_dm_and_attachment(channel_id, message, att):
    """
    Send a new message
    Returns a message object:
    https://discord.com/developers/docs/resources/channel#message-object
    """

    payload_json = {'content': message}
    data = {'payload_json': json.dumps(payload_json)}

    response = do_bot_call_upload(DISCORD_API_URI + CREATE_MESSAGE_ENDPOINT % channel_id, DISCORD_BOT_TOKEN, data=data, file=att, method="POST")

    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def create_channel(parent_id, guild_id, channel_name):
    """
    Create a new channel
    Returns a Channel object:
    https://discord.com/developers/docs/resources/channel#channel-object
    """

    data = {
        'name': channel_name,
        'type': 0,
        'parent_id': parent_id
    }

    response = do_bot_call(DISCORD_API_URI + CREATE_CHANNEL_ENDPOINT % (guild_id), DISCORD_BOT_TOKEN, data=data, method="POST")

    if response.status_code == 201:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def create_thread(channel_id, message_id, thread_name, three_day_thread_archive=False):
    """
    Create a new thread
    Returns a Channel object:
    https://discord.com/developers/docs/resources/channel#channel-object
    """

    data = {
        'name': thread_name,
        'auto_archive_duration': 4320 if three_day_thread_archive else 1440
    }

    response = do_bot_call(DISCORD_API_URI + CREATE_THREAD_ENDPOINT % (channel_id, message_id), DISCORD_BOT_TOKEN, data=data, method="POST")

    if response.status_code == 200:
        return response.json()

    return dict(error=True, error_info=response.content, status_code=response.status_code)

def get_avatar(user_id, avatar):
    """
    Builds avatar URL

    Returns https://cdn.discordapp.com/avatars/184528528572678145/94870f31afbc284723d68eb518d3c2c7.png?size=4096
    """

    url_string = 'avatars/{0}/{1}.png' # 'avatars/{user_id}/{user_avatar}.png'

    return DISCORD_IMAGE_CDN + url_string.format(user_id, avatar)

def get_guild_icon(guild_id, icon):
    """
    Builds icon URL

    Returns https://cdn.discordapp.com/icons/193277318494420992/a_d1db07a58a179eef3f70b7974c86d4dc.png?size=4096
    """

    url_string = 'icons/{0}/{1}.png' # 'icons/guild_id/guild_icon.png'

    return DISCORD_IMAGE_CDN + url_string.format(guild_id, icon)