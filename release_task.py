# -*- coding: utf-8 -*-

## Release Task ##
# Run every minute to free user from the pit #

import sys
import logging
import json
import datetime
import yaml
from typing import Optional
import requests
from urllib.parse import quote as _uriquote
from utils import parse_args, iso_to_datetime

from database import Database
from modules.pitbot.database import PitBotDatabase

log: logging.Logger = logging.getLogger("bot")

BASE = 'https://discord.com/api/v9'
GET_USER_PATH = '/users/{user_id}'
GET_GUILD_PATH = '/guilds/{guild_id}'
CREATE_MESSAGE_PATH = '/channels/{channel_id}/messages'
CREATE_DM_PATH = '/users/@me/channels' # json={"recipient_id": recipient_id}
REMOVE_ROLE_PATH = '/guilds/{guild_id}/members/{user_id}/roles/{role_id}'

def do_api_call(method: str = 'GET', action: str = '/users/@me', token: str = None, headers: Optional[dict] = None, 
	data: dict = dict(), reason: str = None) -> dict:

	if not headers:
		headers = {
			'User-Agent': 'DiscordBot (https://github.com/sakurazaki/discord-continued 1.0) Python/3.9',
			'X-Ratelimit-Precision': 'millisecond',
		}

	headers['Authorization'] = 'Bot ' + token
	headers['Content-Type'] = 'application/json'

	if reason:
		headers['X-Audit-Log-Reason'] = _uriquote(reason, safe='/ ')

	if method == 'GET':
		request = requests.get(BASE + action, headers=headers)

	elif method == 'POST':
		request = requests.post(BASE + action, headers=headers, json=data)

	elif method == 'DELETE':
		request = requests.delete(BASE + action, headers=headers)

	return request.json()

def send_embed_message(channel_id: int, title: str = "", description: str = "", color: int = 0x0aeb06, fields: list = list(),
	footer: dict = None, image: dict= None, token: str = None) -> dict:
	embed = {
		"type": "rich",
		"title": title,
		"description": description,
		"color": color,
		"fields": fields
	}

	if footer is not None:
		embed['footer'] = footer

	if image is not None:
		embed['image'] = image

	data = {'embeds': [embed]}

	message = do_api_call('POST', CREATE_MESSAGE_PATH.format(channel_id=channel_id), token, data=data)

	return message

def send_embed_dm(user_id: int, title: str = "", description: str = "", color: int = 0x0aeb06, fields: list = list(),
	footer: dict = None, image: dict = None, token: str = None) -> dict:

	embed = {
		"type": "rich",
		"title": title,
		"description": description,
		"color": color,
		"fields": fields
	}

	if footer is not None:
		embed['footer'] = footer

	if image is not None:
		embed['image'] = image

	data = {'recipient_id': user_id}
	dm_channel = do_api_call('POST', CREATE_DM_PATH, token, data=data)

	data = {'embeds': [embed]}
	message = do_api_call('POST', CREATE_MESSAGE_PATH.format(channel_id=dm_channel['id']), token, data=data)

	return message

def expire_timeout(pit_db: PitBotDatabase, user: dict) -> Optional[dict]:
	"""
	Sets a timeout as expired
	"""

	params = {'status': 'expired', 'updated_date': datetime.datetime.now().isoformat()}
	query = {'user_id': user['id'], 'status': 'active'}

	timeout = pit_db.update_timeout(params=params, query=query)

	return timeout

def free_users(token: str, config: dict) -> None:

	db = Database(config['database'])
	pit_db = PitBotDatabase(database=db)

	timeouts = pit_db.get_timeouts(query={'status': 'active'}, partial=False)
	guild = db.get_default_guild()
	guild['id'] = guild['guild_id'] # ease of use

	for timeout in timeouts:
		issued_date = iso_to_datetime(timeout['created_date'])
		expire_date = issued_date + datetime.timedelta(seconds=timeout['time'])

		user = timeout.get("user")
		if not user:
			# This is weird because we literally store users with the timeout, but just in case
			user = do_api_call('GET', GET_USER_PATH.format(user_id=timeout['user_id']), token)
		else:
			user['id'] = user['discord_id'] # ease of use

		if timeout['guild_id'] != guild['id']:
			# This should be weird too since its only in a single server
			guild = do_api_call('GET', GET_GUILD_PATH.format(guild_id=timeout['guild_id']), token)

		if datetime.datetime.now() >= expire_date:
			timeout_info = expire_timeout(pit_db, user)

			for role in guild['ban_roles']:
				try:
					do_api_call('DELETE', REMOVE_ROLE_PATH.format(guild_id=guild['id'], user_id=user['id'], role_id=role), 
						token, reason="Timeout expired.")
				except:
					# User left the server, handle it
					pass

			send_embed_message(guild['log_channel'], "User Released", f"User: <@{user['id']}> was just released from the pit.", token=token)

			# Send a DM to the user
			description = f"Your timeout in {guild['name']} has expired and you've been released from the pit."

			image = {
				"url": "https://i.imgur.com/CraIFqD.gif",
				"width": 0,
				"height": 0
			}

			try:
				send_embed_dm(user['id'], "User Timeout", description, image=image, token=token)
			except:
				pass

if __name__ == '__main__':
	args = parse_args()

	try:
		config_file = open('config.yaml', 'r')
		config = yaml.load(config_file, Loader=yaml.FullLoader)

	except FileNotFoundError:
		log.error("\"config.yaml\" has to exist on root directory.")
		sys.exit(0)

	except IOError:
		log.error("PitBot doesn't have the proper permissions to read \"config.yaml\".")
		sys.exit(0)

	free_users(args.token, config)
