# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for, flash, jsonify
from flask_socketio import emit, join_room, leave_room

import datetime
import json
import bson
from bson.objectid import ObjectId

from web_app import socketio
from web_app.config import SERVER_ID
from web_app.utils import rend_folder_template, verify_session, verify_api_session
from web_app.database import Database
from web_app.discord_api import send_message, send_embed_message, send_attachment, create_channel, get_bot_guilds, get_avatar, get_guild_member

modmail_bp = Blueprint('modmail', __name__)

@modmail_bp.route('/modmail', methods=['GET'], endpoint="index")
@verify_session
def index():
    db = Database()

    query = {'status': 'active'}

    if 'status' in request.args:
        query['status'] = request.args['status']

    tickets = db.get_all_tickets(query=query)

    return rend_folder_template('modmail', 'index', tickets=tickets)

@modmail_bp.route('/modmail/tickets/<ticket_id>', methods=['GET'], endpoint="ticket")
@verify_session
def ticket(ticket_id):
    db = Database()

    ticket = db.get_ticket(ticket_id)

    if ticket['status'] != 'active':
        return rend_folder_template('modmail', 'readonly_ticket', ticket=ticket)

    return rend_folder_template('modmail', 'ticket', ticket=ticket)

@modmail_bp.route('/modmail/tickets/<ticket_id>/new_message', methods=['POST'], endpoint="new_ticket_message")
@verify_session
def new_ticket_message(ticket_id):
    attachment = request.files.get('attachment')
    message = request.form.get('message')
    user_id = session['user_id']
    channel_id = request.form['channel_id']

    if not attachment and not message:
        return jsonify({'status': 'OK', 'message': 'Nothing was delivered because there was nothing to deliver.'})

    db = Database()
    user = db.add_user(user_id, col='modmail_users') # note: this doesnt add a user if it already exists. Its a "find and add"
    ticket = db.get_ticket(ticket_id)
    guild = get_bot_guilds()[0]

    embeds = [
        {
            'title': "Message Received",
            'description': message,
            'color': 7419530,
            'type': 'rich',
            'fields': [
                {'name': 'Mod Info', 'value': f"<@{user['discord_id']}>"}
            ],
            'footer': {
                'text': f'{guild["name"]} Mod Team · Ticket: {ticket_id}'
            }
        }
    ]
    new_message = send_embed_message(channel_id, user, embeds=embeds)

    if attachment:
        att = send_attachment(channel_id, attachment)
        new_message['attachments'] = att['attachments']
    
    history = db.add_ticket_message(ticket, new_message, user)

    data = {
        **history,
        **ticket
    }

    data['ticket_id'] = str(data['ticket_id'])
    data['sender'] = 'mod'
    data['user_id'] = str(data['user_id'])
    data['guild_id'] = str(data['guild_id'])
    data['channel_id'] = str(data['channel_id'])
    data['user']['discord_id'] = str(data['user']['discord_id'])

    return jsonify({'status': 'OK', 'data': data})

@modmail_bp.route('/modmail/tickets/<ticket_id>/close', methods=['POST'], endpoint="close_ticket")
@verify_session
def close_ticket(ticket_id):
    data = request.form.to_dict()

    db = Database()
    ticket = db.close_ticket(ticket_id, session['user_id'], data)
    ticket = db.get_ticket(ticket_id)
    mod = db.add_user(session['user_id'])
    guild = get_bot_guilds()[0]

    closing_comment = 'No reason specified'

    if data['closed_comment']:
        closing_comment = data['closed_comment']

    embeds = [
        {
            'title': "Ticket closed",
            'description': f"Ticket {ticket_id} was closed.",
            'color': 10038562,
            'type': 'rich',
            'fields': [
                {'name': 'Closing Reason', 'value': closing_comment},
                {'name': 'Mod Info', 'value': f"<@{session['user_id']}>"}
            ],
            'footer': {
                'text': f'{guild["name"]} Mod Team · Ticket: {ticket_id}'
            }
        }
    ]
    new_message = send_embed_message(ticket['channel_id'], mod, embeds=embeds)

    # notify server
    guild_config = db.get_guild_config(guild['id'])

    channel_id = guild_config.get('modmail_channel')
    if not channel_id:
        channel_id = guild_config.get('log_channel')
    if not channel_id:
        flash("Ticket closed succesfully.", 'success')
        return redirect(url_for('modmail.index'))

    embeds = [
        {
            'title': "Ticket closed",
            'description': f"Ticket {ticket_id} was closed.",
            'color': 10038562,
            'type': 'rich',
            'fields': [
                {'name': 'Closing Reason', 'value': closing_comment},
                {'name': 'Mod Info', 'value': f"<@{session['user_id']}>"}
            ],
            'footer': {
                'text': f"{ticket['user']['username']}#{ticket['user']['username_handle']} · Ticket ID {ticket_id}",
                'icon_url': get_avatar(ticket['user']['discord_id'], ticket['user']['avatar'])
            }
        }
    ]
    new_message = send_embed_message(channel_id, mod, embeds=embeds)

    flash("Ticket closed succesfully.", 'success')
    return redirect(url_for('modmail.index'))

@modmail_bp.route('/modmail/tickets/<ticket_id>/delete', methods=['POST'], endpoint="delete_ticket")
@verify_session
def delete_ticket(ticket_id):
    data = request.form.to_dict()

    db = Database()
    ticket = db.delete_ticket(ticket_id)
    mod = db.add_user(session['user_id'])
    guild = get_bot_guilds()[0]

    closing_comment = 'No reason specified'

    if data['closed_comment']:
        closing_comment = data['closed_comment']

    embeds = [
        {
            'title': "Ticket closed",
            'description': f"Ticket {ticket_id} was closed.",
            'color': 10038562,
            'type': 'rich',
            'fields': [
                {'name': 'Closing Reason', 'value': closing_comment},
                {'name': 'Mod Info', 'value': f"<@{session['user_id']}>"}
            ],
            'footer': {
                'text': f'{guild["name"]} Mod Team · Ticket: {ticket_id}'
            }
        }
    ]
    new_message = send_embed_message(ticket['channel_id'], mod, embeds=embeds)

    # notify server
    guild_config = db.get_guild_config(guild['id'])

    channel_id = guild_config.get('modmail_channel')
    if not channel_id:
        channel_id = guild_config.get('log_channel')
    if not channel_id:
        flash("Ticket closed succesfully.", 'success')
        return redirect(url_for('modmail.index'))

    embeds = [
        {
            'title': "Ticket closed",
            'description': f"Ticket {ticket_id} was closed.",
            'color': 10038562,
            'type': 'rich',
            'fields': [
                {'name': 'Closing Reason', 'value': closing_comment},
                {'name': 'Mod Info', 'value': f"<@{session['user_id']}>"}
            ],
            'footer': {
                'text': f"{ticket['user']['username']}#{ticket['user']['username_handle']} · Ticket ID {ticket_id}",
                'icon_url': get_avatar(ticket['user']['discord_id'], ticket['user']['avatar'])
            }
        }
    ]
    new_message = send_embed_message(channel_id, mod, embeds=embeds)

    flash("Ticket closed succesfully.", 'success')
    return redirect(url_for('modmail.index'))

@modmail_bp.route('/modmail/tickets/<ticket_id>/reopen', methods=['GET'], endpoint="reopen_ticket")
@verify_session
def reopen_ticket(ticket_id):
    data = request.form.to_dict()

    db = Database()
    ticket = db.reopen_ticket(ticket_id)
    user = db.add_user(session['user_id'])
    guild = get_bot_guilds()[0]

    embeds = [
        {
            'title': "Ticket reopened",
            'description': f"Ticket {ticket_id} was reopened.",
            'color': 7419530,
            'type': 'rich',
            'fields': [
                {'name': 'Mod Info', 'value': f"<@{session['user_id']}>"}
            ],
            'footer': {
                'text': f'{guild["name"]} Mod Team · Ticket: {ticket_id}'
            }
        }
    ]
    new_message = send_embed_message(ticket['channel_id'], user, embeds=embeds)

    flash("Ticket reopened succesfully.", 'success')
    return redirect(url_for('modmail.ticket', ticket_id=ticket_id))

@modmail_bp.route('/modmail/publish/<ticket_id>', methods=['POST'], endpoint="api_publish_ticket")
@verify_api_session
def api_publish_ticket(ticket_id):
    db = Database()
    ticket = db.get_ticket(ticket_id)
    user = ticket['user']
    guild = get_bot_guilds()
    guild_id = None
    if not guild or not isinstance(guild, list):
        guild_id = SERVER_ID
    elif len(guild) == 0:
        guild_id = SERVER_ID
    else:
        guild_id = guild[0]['id']
    guild_config = db.get_guild_config(guild_id)

    channel_id = guild_config.get('modmail_channel')
    category_id = guild_config.get('modmail_category')

    if not channel_id:
        channel_id = guild_config.get('log_channel')
    if not channel_id:
        return jsonify({'status': 'Error', 'message': 'Modmail channel is not setup correctly.'}), 400

    if not category_id:
        return jsonify({'status': 'Error', 'message': 'Modmail category is not setup correctly.'}), 400

    url = url_for('modmail.ticket', ticket_id=ticket_id, _external=True)

    embeds = [
        {
            'title': "New Ticket",
            'color': 2067276,
            'type': 'rich',
            'fields': [
                {'name': 'Info', 'value': f"You can view full details and work further in the Ticket dashboard:\r\n\r\n{url}"},
            ],
            'footer': {
                'text': f"{ticket['user']['username']}#{ticket['user']['username_handle']} · Ticket ID {ticket_id}",
                'icon_url': get_avatar(ticket['user']['discord_id'], ticket['user']['avatar'])
            }
        }
    ]
    new_message = send_embed_message(channel_id, user, embeds=embeds)

    # Publish channel
    channel = create_channel(category_id, guild_id, ticket_id)

    # update ticket with newly created channel id
    db.update_ticket(ticket_id, {'modmail_channel_id': bson.Int64(channel['id'])})

    member_info = get_guild_member(guild_id, ticket['user']['discord_id'])

    roles = " ".join([f"<@&{role_id}>" for role_id in member_info['roles']])

    embeds = [
        {
            'title': "New Ticket",
            'description': f'Type a message in this channel to reply. Messages starting with the server prefix `{guild_config["modmail_character"]}`\
                are ignored, and can be used for staff discussion. User the command `{guild_config["modmail_character"]}close <reason:optional>` to\
                close the ticket.',
            'color': 2067276,
            'type': 'rich',
            'fields': [
                {'name': 'User', 'value': f"<@{ticket['user']['discord_id']}> ({ticket['user']['discord_id']})", 'inline': True},
                {'name': 'Roles', 'value': roles, 'inline': True},
                {'name': 'Dashboard', 'value': f"You can view full details and work further in the Ticket dashboard:\r\n\r\n{url}"}
            ],
            'footer': {
                'text': f"{ticket['user']['username']}#{ticket['user']['username_handle']} · Ticket ID {ticket_id}",
                'icon_url': get_avatar(ticket['user']['discord_id'], ticket['user']['avatar'])
            }
        }
    ]
    new_message = send_embed_message(channel['id'], user, embeds=embeds)

    return jsonify({'status': 'OK', 'message': 'Ticket published correctly.'})

@modmail_bp.route('/modmail/publish/<ticket_id>/message', methods=['POST'], endpoint="api_publish_message")
@verify_api_session
def api_publish_message(ticket_id):
    data = {'ticket_id': ticket_id, **request.json}
    # Change discord ID to string because javascript overflows
    data['user_id'] = str(data['user_id'])
    data['guild_id'] = str(data['guild_id'])
    data['user']['discord_id'] = str(data['user']['discord_id'])
    data['sender'] = 'user'
    socketio.emit('dm_message', data, namespace='/feed', broadcast=True, to=ticket_id)
    return jsonify({'status': 'OK', 'message': 'Message published correctly.'})

@socketio.on('connected', namespace="/feed")
def handle_dm_message(message):
    join_room(message['ticket_id'])
    emit('connected', {'message': f'Connected to: {message["ticket_id"]}'}, to=message['ticket_id'])

@socketio.on('message', namespace="/feed")
def handle_dm_message(message):
    emit('new_dm', message, to=message['ticket_id'])
