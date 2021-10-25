# -*- coding: utf-8 -*-

## Database Module ##
# Connect to database and prepare a connection. #

from datetime import datetime
import discord, bson
from bson.objectid import ObjectId

from .db import get_conn

class ModmailDatabase:

	def __init__(self, config):
		"""Create and configure a connection to database.

		Provide with wrapper for database
		"""

		self._db_config = config
		self._conn = get_conn(config['path'])
		self._db = self._conn[config['db_name']]

	def close(self):
		"""Close connection to database"""
		self._conn.close()

	# Ticket related
	def get_user_ticket(self, user):
		"""
		Given an user, return information about their ticket

		@user: typeof Discord.Author

		returns: ticket information or empty dict if None
		"""

		col = self._db['modmail_tickets']

		ticket = col.find_one({'user_id': user.id, 'status': 'active'})
		if ticket is None:
			return dict()

		col = self._db['modmail_users']
		ticket['user'] = col.find_one({'discord_id': user.id})

		return ticket

	def get_ticket(self, params):
		"""
		Given search parameters, return ticket associated to it

		@params: typeof Dictionary

		returns: ticket information or empty dict if None
		"""

		col = self._db['modmail_tickets']

		for arg in params:
			if isinstance(params[arg], int):
				params[arg] = bson.Int64(params[arg])

			if arg == "_id":
				params[arg] = ObjectId(params[arg])

		ticket = col.find_one(params)
		if ticket is None:
			return dict()

		col = self._db['modmail_users']
		ticket['user'] = col.find_one({'discord_id': bson.Int64(ticket['user_id'])})

		return ticket

	def create_ticket(self, user, channel, guild):
		"""
		Given a user channel and guild, make a new ticket.

		@user: typeof Discord.User
		@channel: typeof Discord.Channel
		@guild: typeof Discord.Guild

		returns: ticket
		"""

		col = self._db['modmail_tickets']
		ticket = col.find_one({'user_id': user.id, 'status': 'active'})

		if ticket is None:
			ticket = {
				'user_id': bson.Int64(user.id),
				'status': 'active',
				'channel_id': bson.Int64(channel.id),
				'guild_id': bson.Int64(guild['guild_id']),
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat(),
				'closed_date': None,
				'closed_user_id': None,
				'closed_comment': None,
				'action_taken': None
			}

			result = col.insert_one(ticket)
			ticket['_id'] = result.inserted_id

		col = self._db['modmail_users']
		mm_user = col.find_one({'discord_id': user.id})

		if mm_user is None:
			avatar = user.avatar

			if isinstance(user.avatar, discord.asset.Asset):
				avatar = user.avatar.key

			mm_user = {
				'discord_id': bson.Int64(user.id),
				'username': user.name,
				'username_handle': user.discriminator,
				'avatar': avatar,
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat()
			}

			result = col.insert_one(mm_user)
			mm_user['_id'] = result.inserted_id

		ticket['user'] = mm_user
		ticket['guild'] = guild

		return ticket

	def add_ticket_message(self, ticket, message, user):
		"""
		Given a ticket, message and user add an entry to the ticket history.

		@ticket: ticket dictionary from database
		@message: typeop Discord.Message
		@user: typeof Discord.User

		returns: entry history
		"""

		col = self._db['modmail_users']
		mm_user = col.find_one({'discord_id': user.id})
		if mm_user is None:
			avatar = user.avatar

			if isinstance(user.avatar, discord.asset.Asset):
				avatar = user.avatar.key

			mm_user = {
				'discord_id': bson.Int64(user.id),
				'username': user.name,
				'username_handle': user.discriminator,
				'avatar': avatar,
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat()
			}

			result = col.insert_one(mm_user)
			mm_user['_id'] = result.inserted_id

		col = self._db['modmail_history']
		entry = {
			'ticket_id': ticket['_id'],
			'user_id': bson.Int64(user.id),
			'message': message.content,
			'attachments': list(),
			'created_date': datetime.now().isoformat(),
			'updated_date': datetime.now().isoformat()
		}

		for att in message.attachments:
			entry['attachments'].append({
				'content_type': att.content_type,
				'filename': att.filename,
				'id': att.id,
				'size': att.size,
				'url': att.url
			})

		result = col.insert_one(entry)
		entry['_id'] = result.inserted_id

		return entry

	def close_ticket(self, ticket_id, user_id, data):
		"""
		Given a ticket_id, user_id and data close a given ticket.

		@ticket_id: string, ticket_id
		@user_id: discord user_id
		@data: params to update

		returns: ticket
		"""

		col = self._db['modmail_tickets']

		data['updated_date'] = datetime.now().isoformat()
		data['closed_date'] = datetime.now().isoformat()
		data['closed_user_id'] = bson.Int64(user_id)
		data['status'] = 'closed'

		result = col.find_one_and_update({'_id': ObjectId(ticket_id)}, {"$set" : data })

		return result


if __name__ == '__main__':
	import pprint

	config = {
		'path': 'mongodb://sakurazaki:testpasswd@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false',
		'db_name': 'moon2web'
	}

	conn = get_conn(config['path'])
	conn.close()
