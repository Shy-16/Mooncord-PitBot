# -*- coding: utf-8 -*-

## Database Module ##
# Connect to database and prepare a connection. #

import logging
import datetime
from pymongo import MongoClient, ReturnDocument
import bson
from bson.objectid import ObjectId

from web_app.config import DB_PATH, DB_NAME
import web_app.discord_api as discord_api


_connection = None

def get_conn(path):
    """
    Get a DB object.
    
    """

    # check to see if we exist already (singleton!)

    global _connection   # pylint: disable=global-statement

    if _connection is not None:
    	# Do cleanup if necessary
        return _connection

    # create a new instance
    _connection = MongoClient(path)
    logging.info(f"Created new connection to database.")

    return _connection


class Database:

	def __init__(self):
		"""Create and configure a connection to database.

		Provide with wrapper for database
		"""

		self._conn = get_conn(DB_PATH)
		self._db = self._conn[DB_NAME]

	def close(self):
		"""Close connection to database"""
		self._conn.close()

	def do_query(self, col, query):
		"""
		Execute given query in given collection.

		@col: string collection
		@query: dictionary query

		returns: Cursor with information
		"""

		col = self._db[col]
		return col.find(query)

	def find_one(self, col, query):
		"""
		Execute given query in given collection and return only one.

		@col: string collection
		@query: dictionary query

		returns: Cursor with information
		"""

		col = self._db[col]
		return col.find_one(query)

	def count_documents(self, col, query):
		"""
		Counter the number of documents in given collection.

		@col: string collection
		@query: dictionary query

		returns: string, count
		"""

		col = self._db[col]
		return col.count_documents(query)

	# Get Timeout Information
	def get_all_timeouts(self, status='active', from_date=None):
		"""
		Get all current active timeouts

		returns: list of timeouts
		"""

		col = self._db['users_bans']

		query = dict()

		if status != 'both':
			query['status'] = status

		if from_date is not None:
			query['created_date'] = {'$gte': from_date}

		results = col.find(query)
		results = list(results)

		col = self._db['users']

		for result in results:
			result['user'] = col.find_one({'discord_id': result['user_id']})
			result['issuer'] = col.find_one({'discord_id': result['issuer_id']})
			if not result['issuer']:
				result['issuer'] = self.add_user(result['issuer_id'])
			result['formatted_time'] = datetime.datetime.fromisoformat(result['created_date']).strftime("%m/%d/%Y %H:%M")

		return results

	# Get Strikes Information
	def get_all_strikes(self, status='active', from_date=None):
		"""
		Get all strikes

		returns: list of strikes
		"""

		col = self._db['users_strikes']

		query = dict()

		if status != 'both':
			query['status'] = status

		if from_date is not None:
			query['created_date'] = {'$gte': from_date}

		results = col.find(query)
		results = list(results)

		col = self._db['users']

		for result in results:
			result['user'] = col.find_one({'discord_id': result['user_id']})
			result['issuer'] = col.find_one({'discord_id': result['issuer_id']})
			if not result['issuer']:
				result['issuer'] = self.add_user(result['issuer_id'])
			result['formatted_time'] = datetime.datetime.fromisoformat(result['created_date']).strftime("%m/%d/%Y %H:%M")

		return results

	# Users related
	def add_user(self, user_id, col='users'):
		"""
		Given a user_id add a user to the database

		@user_id: int - discord_id

		returns: user

		"""

		col = self._db[col]

		user = col.find_one({'discord_id': bson.Int64(user_id)})

		if user is None:
			discord_user = discord_api.get_user(user_id)

			user = {
				'discord_id': bson.Int64(discord_user['id']),
				'username': discord_user['username'],
				'username_handle': discord_user['discriminator'],
				'display_name': discord_user['username'],
				'avatar': discord_user['avatar'],
				'verified': discord_user.get('verified'),
				'premium_type': discord_user.get('premium_type'),
				'created_date': datetime.datetime.now().isoformat(),
				'updated_date': datetime.datetime.now().isoformat()
			}

			result = col.insert_one(user)
			user['_id'] = result.inserted_id

		return user

	def get_users(self):
		"""
		Return all users in database

		returns: Cursor
		"""

		col = self._db['users']

		user = col.find()

		return user

	# Modmail related
	def get_ticket(self, ticket_id):
		"""
		Given a ticket_id get information about the ticket

		@ticket_id: int - ticket_id

		returns: ticket

		"""

		col = self._db['modmail_tickets']

		ticket = col.find_one({'_id': ObjectId(ticket_id)})

		if ticket:
			ticket['users'] = list()
			user_ids = list()

			col = self._db['modmail_users']
			ticket['user'] = col.find_one({'discord_id': ticket['user_id']})
			ticket['user']['_id'] = str(ticket['user']['_id'])

			if ticket['status'] == 'closed':
				ticket['closing_user'] = col.find_one({'discord_id': bson.Int64(ticket['closed_user_id'])})
				ticket['closing_user']['_id'] = str(ticket['closing_user']['_id'])

			col = self._db['modmail_history']
			ticket['history'] = list(col.find({'ticket_id': ticket['_id']}))

			col = self._db['modmail_users']
			for entry in ticket['history']:
				entry['_id'] = str(entry['_id'])
				entry['ticket_id'] = str(entry['ticket_id'])
				entry['user'] = self.add_user(entry['user_id'], col='modmail_users')
				entry['user']['_id'] = str(entry['user']['_id'])
				if entry['user_id'] != ticket['user_id'] and entry['user_id'] not in user_ids:
					ticket['users'].append(entry['user'])
					user_ids.append(entry['user_id'])

		ticket['_id'] = str(ticket['_id'])
		return ticket

	def get_user_ticket(self, user_id):
		"""
		Given a user_id get any active tickets

		@user_id: int - discord_id

		returns: ticket

		"""

		col = self._db['modmail_tickets']

		ticket = col.find_one({'user_id': user_id, 'status': 'active'})

		if ticket:
			col = self._db['modmail_users']

			ticker['user'] = col.find_one({'discord_id': user_id})

		return ticket

	def get_all_tickets(self, query={'status': 'active'}):
		"""
		Given a filter get all tickets

		returns: ticket

		"""

		col = self._db['modmail_tickets']

		results = col.find(query)
		results = list(results)

		for result in results:
			col = self._db['modmail_users']
			result['user'] = col.find_one({'discord_id': result['user_id']})

			col = self._db['modmail_history']
			result['history'] = list(col.find({'ticket_id': result['_id']}))

		return results

	def update_ticket(self, ticket_id, params):
		"""
		Given a ticket, update database with given params.

		@ticket_id: integer ticket_id
		@params: dictionary with new values

		returns: entry history
		"""

		col = self._db['modmail_tickets']

		result = col.find_one_and_update({'_id': ObjectId(ticket_id)},
			{"$set" : params }
		)
		if result is None:
			result = dict()

		return result

	def add_ticket_message(self, ticket, message, user):
		"""
		Given a ticket, message and user add an entry to the ticket history.

		@ticket: ticket dictionary from database
		@message: typeop Discord.Message
		@user: typeof Discord.User

		returns: entry history
		"""

		text = message['content']

		if not text:
			text = message['embeds'][0]['description']

		col = self._db['modmail_history']
		entry = {
			'ticket_id': ObjectId(ticket['_id']),
			'user_id': bson.Int64(user['discord_id']),
			'message': text,
			'attachments': list(),
			'created_date': datetime.datetime.now().isoformat(),
			'updated_date': datetime.datetime.now().isoformat()
		}

		for att in message['attachments']:
			entry['attachments'].append({
				'content_type': att['content_type'],
				'filename': att['filename'],
				'id': att['id'],
				'size': att['size'],
				'url': att['url']
			})

		result = col.insert_one(entry)
		entry['_id'] = result.inserted_id
		entry['_id'] = str(entry['_id'])
		entry['ticket_id'] = str(entry['ticket_id'])

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

		data['updated_date'] = datetime.datetime.now().isoformat()
		data['closed_date'] = datetime.datetime.now().isoformat()
		data['closed_user_id'] = bson.Int64(user_id)
		data['status'] = 'closed'

		result = col.find_one_and_update({'_id': ObjectId(ticket_id)}, {"$set" : data })

		return result

	def delete_ticket(self, ticket_id):
		"""
		Given a ticket_id delete it from database

		@ticket_id: string, ticket_id

		returns: ticket
		"""

		col = self._db['modmail_tickets']

		ticket = col.find_one_and_delete({'_id': ObjectId(ticket_id)})

		if ticket:
			col = self._db['modmail_users']
			ticket['user'] = col.find_one({'discord_id': ticket['user_id']})
			ticket['user']['_id'] = str(ticket['user']['_id'])

		return ticket

	def reopen_ticket(self, ticket_id):
		"""
		Given a ticket_id reopen it

		@ticket_id: string, ticket_id

		returns: ticket
		"""

		col = self._db['modmail_tickets']

		result = col.find_one_and_update({'_id': ObjectId(ticket_id)}, {"$set" : {'status': 'active'} })

		return result

	# Guild related
	def get_guild_config(self, guild_id):
		"""
		Given a ticket_id reopen it

		@ticket_id: string, ticket_id

		returns: ticket
		"""

		col = self._db['discord_config']

		result = col.find_one({'guild_id': bson.Int64(guild_id)})

		return result

	# Banwords related
	def get_banwords(self, guild_id, query=None):
		"""
		Given a guild_id return all banwords associated with it

		@guild_id: Int64, guild_id

		returns: list of Banword
		"""

		col = self._db['banwords']

		params = {'guild_id': bson.Int64(guild_id)}

		if query is not None:
			params.update(query)

		results = col.find(params)

		return list(results)

	def add_banword(self, guild_id, data):
		"""
		Given data add banword to database

		@data: json-like data, information of banword

		returns: Banword with ID included
		"""

		# Data example:
		# {'word': 'retard', 'duration': 7200, 'delete_message': True, 'variable_time': True, 
		# 'temporary_ban': False, 'permanent_ban': False, 'include_link': True, user_id': '539881999926689829'}

		col = self._db['banwords']

		entry = {
			'guild_id': bson.Int64(guild_id),
			'user_id': bson.Int64(data['user_id']),
			'word': data['word'],
			'duration': data['duration'],
			'strength': data['strength'],
			'delete_message': data['delete_message'],
			'variable_time': data['variable_time'],
			'temporary_ban': data['temporary_ban'],
			'permanent_ban': data['permanent_ban'],
			'include_link':  data['include_link'],
			'active': True,
			'created_date': datetime.datetime.now().isoformat(),
			'updated_date': datetime.datetime.now().isoformat()
		}

		result = col.insert_one(entry)

		entry['_id'] = result.inserted_id

		return entry

	def get_banword(self, banword_id):
		"""
		Given a banword_id get a banword with that ID

		@banword_id: ID of banword

		returns: Banword
		"""

		col = self._db['banwords']

		result = col.find_one({'_id': ObjectId(banword_id)})

		return result

	def put_banword(self, banword_id, data):
		"""
		Given a banword_id and data update banword of ID with given data

		@banword_id: ID of banword
		@data: json like of update data

		returns: Banword
		"""

		col = self._db['banwords']

		result = col.find_one_and_update({'_id': ObjectId(banword_id)},
			{"$set" : data }, return_document=ReturnDocument.AFTER
		)

		if result is None:
			result = dict()

		return result

	def delete_banword(self, banword_id):
		"""
		Given a banword_id delete a banword with that ID

		@banword_id: ID of banword

		returns: deleted banword
		"""

		col = self._db['banwords']

		result = col.find_one_and_delete({'_id': ObjectId(banword_id)})

		return result

if __name__ == '__main__':
	import pprint

	config = {
		'path': 'mongodb://sakurazaki:testpwd@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false',
		'db_name': 'moon2web'
	}

	# db = new Database()

	conn = get_conn(config['path'])
	db = conn[config['db_name']]
	col = db['users']

	col.insert_one({
		'discord_id': 5549,
		'username': 'Test_user',
		'username_handle': '0001',
		'display_name': 'Test User',
		'avatar': None,
		'verified': True,
		'premium_type': None,
		'created_date': datetime.datetime.now().isoformat(),
		'updated_date': datetime.datetime.now().isoformat()
	})

	result = col.find_one({'discord_id': 5549})
	pprint.pprint(result)

	col = db['users_bans']
	results = col.find({'user_id': 539881999926689829})

	for res in results:
		pprint.pprint(res)

	col = db['users']
	col.find_one_and_delete({'discord_id': 5549})

	conn.close()
