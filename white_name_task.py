# -*- coding: utf-8 -*-

## Purge Task ##
# Run every night to check for white names and remind them to resub #

import sys
import logging
import time
from typing import Optional
import urllib.parse
from urllib.parse import quote as _uriquote
from pathlib import Path
import yaml
import requests

from utils import parse_args

from database import Database

log: logging.Logger = logging.getLogger("bot")

BASE = 'https://discord.com/api/v9'
GET_USER_PATH = '/users/{user_id}'
GET_GUILD_PATH = '/guilds/{guild_id}'
GET_GUILD_MEMBERS_PATH = '/guilds/{guild_id}/members'
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

def get_user_batch(limit: int = 1000, last_id: Optional[str] = None, guild_id: str = '', token: str = '') -> list:

	params = {
		'limit': limit
	}

	if last_id:
		params['after'] = last_id

	URL = GET_GUILD_MEMBERS_PATH.format(guild_id=guild_id) + '?' + urllib.parse.urlencode(params)

	users = do_api_call('GET', URL, token)

	return users

def remove_unsub_roles(token: str, config: dict) -> None:

	db = Database(config['database'])

	guild = db.get_default_guild()
	guild['id'] = guild['guild_id'] # ease of use

	# roles are both SPENDIES and GOODWILL
	sub_roles = guild['sub_roles']

	last_length = 1000
	last_id = None

	purge_count = 0

	while last_length >= 1000:
		# users is a list of X discord users sorted by user['id']
		users = get_user_batch(limit=1000, last_id=last_id, guild_id=guild['id'], token=token)

		# update last length to know if we continue the loop
		last_length = len(users)
		last_id = users[-1]['user']['id']

		for user in users:
			# first check if they have at least one of the roles
			needs_purge = len([role for role in user['roles'] if role in sub_roles]) <= 0
			user_roles = db.get_stored_roles(user['user']['id'], guild['id'])

			if needs_purge and not user_roles:
				# store the roles in database
				db.store_roles(user, guild['id'])

				# remove all roles
				for role in user['roles']:
					try:
						do_api_call('DELETE', REMOVE_ROLE_PATH.format(guild_id=guild['id'], user_id=user['user']['id'], role_id=role), 
							token, reason="Sub to moon expired.")
					except:
						# User left the server, handle it
						pass

				# Send a DM to the user
				description = f"Your subscription to Moonmoon has expired.\r\n\r\n Please resubscribe to avoid being kicked in the next Twitch subscriber sync by Discord."

				try:
					send_embed_dm(user['user']['id'], "Sub Expired", description, token=token)
				except:
					pass

				purge_count += 1

			# rate limit is 50 per second, sleep here for 0.1s
			# remove 4 roles + dm = 6 queries. limit would be 9 users per second so ratelimit to 8.
			time.sleep(0.125)

	if purge_count > 0:
		send_embed_message(guild['log_channel'], "Purged users", f"User: {purge_count} users got their roles removed \
		and are waiting for resub or kicking.", token=token)

if __name__ == '__main__':
	args = parse_args()

	base_path = Path(__file__).parent
	file_path = (base_path / 'config.yaml').resolve()

	try:
		config_file = open(file_path, 'r')
		config = yaml.load(config_file, Loader=yaml.FullLoader)

	except FileNotFoundError:
		log.error("\"config.yaml\" has to exist on root directory.")
		sys.exit(0)

	except IOError:
		log.error("PitBot doesn't have the proper permissions to read \"config.yaml\".")
		sys.exit(0)

	remove_unsub_roles(args.token, config)

# example_of_user = {
#     "roles": [
#       "901714190673252393",
#       "901714190673252394",
#       "892913927665618965"
#     ],
#     "nick": null,
#     "avatar": null,
#     "premium_since": null,
#     "joined_at": "2020-03-12T23:40:08.609000+00:00",
#     "is_pending": false,
#     "pending": false,
#     "communication_disabled_until": null,
#     "flags": 0,
#     "user": {
#       "id": "98928803555852288",
#       "username": "SolidlySnake",
#       "avatar": "f180f65df65ac151520645c6bc3728f4",
#       "avatar_decoration": null,
#       "discriminator": "3486",
#       "public_flags": 0
#     },
#     "mute": false,
#     "deaf": false
# }