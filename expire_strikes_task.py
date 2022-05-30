# -*- coding: utf-8 -*-

## Release Task ##
# Run every 24h to remove strikes from people #

import sys
import logging
import json
import datetime
import yaml
from typing import Optional
import requests
from pathlib import Path

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

def do_api_call(method: str = 'GET', action: str = '/users/@me', token: str = None, headers: Optional[dict] = None, 
	data: dict = dict(), reason: str = None) -> dict:

	if not headers:
		headers = {
			'User-Agent': 'DiscordBot (https://github.com/sakurazaki/discord-continued 1.3) Python/3.9',
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

def expire_strike(pit_db: PitBotDatabase, user_id: str, strike_id: int) -> Optional[dict]:
	"""
	Sets a strike as expired
	"""

	params = {'status': 'expired', 'updated_date': datetime.datetime.now().isoformat()}
	query = {'_id': strike_id, 'user_id': user_id, 'status': 'active'}

	strike = pit_db.update_strike(params=params, query=query)

	return strike

def review_strikes(token: str, config: dict) -> None:
	db = Database(config['database'])
	pit_db = PitBotDatabase(database=db)
	now = datetime.datetime.now()
	total_expired_strikes = 0

	# get all strikes that are older than a month and still active
	min_date = datetime.datetime.now() - datetime.timedelta(days=30)

	strikes = pit_db.get_strikes(query={'status': 'active', 'created_date': {'$lte': min_date.isoformat()}}, partial=False)
	guild = db.get_default_guild()
	guild['id'] = guild['guild_id'] # ease of use

	# Compile a unique list of user_ids to iterate from
	users = set([strike['user_id'] for strike in strikes])

	for user_id in users:
		# We need to get all active strikes for the user and compare dates
		user_strikes = pit_db.get_strikes(query={'status': 'active', 'user_id': user_id}, sort=('_id', -1))
		expired_strikes = pit_db.get_strikes(query={'status': 'expired', 'user_id': user_id}, sort=('_id', -1))
		last_strike_date = iso_to_datetime('2000-01-01T00:00:00.000000') # set this to some old ass date.
		if len(expired_strikes) > 0:
			last_strike_date = iso_to_datetime(expired_strikes[0]['updated_date'])

		# get newest strike date
		strike_date = iso_to_datetime(user_strikes[0]['created_date'])

		# if the amount of time between newest strike and today is greater than a month
		# and the amount of time between the last expired strike updated_date and today is greater than a month
		# , delete oldest strike
		# >>> datetime.timedelta(days=30).total_seconds() >>> 2592000.0
		if (now-strike_date).total_seconds() >= 2592000.0 and (now-last_strike_date).total_seconds() >= 2592000.0:
			strike_info = expire_strike(pit_db, user_id, user_strikes[-1]['_id'])
			total_expired_strikes += 1

			# Send a DM to the user
			description = f"A month has passed in {guild['name']} since your last strike so your oldest strike has been forgiven.\r\n\r\n\
			To avoid future strikes please make sure you read our guidelines in <#195682372618813441> and..."

			image = {
				"url": "https://i.imgur.com/Nkdl228.gif",
				"width": 0,
				"height": 0
			}

			try:
				send_embed_dm(user_id, "Strike Info", description, image=image, token=token)
			except Exception as e:
				log.error(e)
				pass

	if total_expired_strikes > 0:
		send_embed_message(guild['log_channel'], "Strikes Expired", f"Today **{total_expired_strikes}** strikes expired.", token=token)

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

	review_strikes(args.token, config)
