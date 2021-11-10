
## Database Module ##
# Connect to database and prepare a connection. #

import logging
from datetime import datetime
from pymongo import MongoClient
import bson
from bson.objectid import ObjectId

from typing import Union, List, Optional

log: logging.Logger = logging.getLogger("database")

class PitBotDatabase:

	def __init__(self, *, database):
		self._db = database._db

	def close(self):
		self._db.close()

	# Timeouts
	def get_timeout(self, query: dict) -> Optional[dict]:
		"""
		Return information about a single timeout.

		In the case of being multiple it will always return the first.
		"""

		col = self._db['users_timeouts']

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		result = col.find_one(query)

		return result

	def get_timeouts(self, query: dict) -> List[dict]:
		"""
		Return information about timeout(s)
		"""

		col = self._db['users_timeouts']

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		results = col.find(query)

		return results

	def create_timeout(self, user: dict, guild_id: int, time: int, 
		issuer_id: int = None, reason: Optional[str] = None) -> dict:
		"""
		Create a new timeout in the database.
		"""

		col = self._db['users']

		db_user = col.find_one({'discord_id': bson.Int64(user['id'])})

		if db_user is None:
			db_user = {
				'discord_id': bson.Int64(user['id']),
				'username': user['username'],
				'username_handle': user['discriminator'],
				'avatar': user['avatar'],
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat()
			}

			result = col.insert_one(db_user)
			db_user['_id'] = result.inserted_id

		col = self._db['users_timeouts']
		timeout_info = {
			'user_db_id': db_user['_id'],
			'user_id': bson.Int64(db_user['discord_id']),
			'guild_id': bson.Int64(guild_id),
			'issuer_id': None,
			'reason': 'No reason specified',
			'time': int(time),
			'status': 'active',
			'created_date': datetime.now().isoformat(),
			'updated_date': datetime.now().isoformat()
		}

		if issuer_id is not None:
			timeout_info['issuer_id'] = bson.Int64(issuer_id)

		if reason is not None:
			timeout_info['reason'] = reason

		result = col.insert_one(timeout_info)
		timeout_info['_id'] = result.inserted_id

		return timeout_info

	def update_timeout(self, *, params: dict, query: dict = None, user_id: dict = None) -> Optional[dict]:
		"""
		Update a timeout from database.
		"""

		col = self._db['users_timeouts']

		if query is None and user_id is None:
			raise Exception("query and user_id cannot be None")

		if query is None:
			query = dict()

		if user_id is not None:
			query['user_id'] = user_id

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		for key in params:
			if key == '_id':
				params[key] = ObjectId(params[key])

			elif '_id' in key:
				params[key] = bson.Int64(params[key])

		result = col.find_one_and_update(query, {"$set" : params })

		return result

	def delete_timeout(self, *, query: dict = None, user_id: dict = None) -> Optional[dict]:
		"""
		Delete a timeout from database.
		"""

		col = self._db['users_timeouts']

		if query is None and user_id is None:
			raise Exception("query and user_id cannot be None")

		if query is None:
			query = dict()

		if user_id is not None:
			query['user_id'] = user_id

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		result = col.find_one_and_delete(query, sort=[('_id', -1)])

		return result

	# Strikes
	def get_strikes(self, query: dict) -> List[dict]:
		"""
		Return information about timeout(s)
		"""

		col = self._db['users_strikes']

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		results = col.find(query)

		return results

	def create_strike(self, user: dict, guild_id: int, issuer_id: int,
		reason: Optional[str] = 'No reason specified') -> dict:
		"""
		Given a member, add a strike to them.
		"""

		col = self._db['users']

		db_user = col.find_one({'discord_id': bson.Int64(user['id'])})

		if db_user is None:
			db_user = {
				'discord_id': bson.Int64(user['id']),
				'username': user['username'],
				'username_handle': user['discriminator'],
				'avatar': user['avatar'],
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat()
			}

			result = col.insert_one(db_user)
			db_user['_id'] = result.inserted_id

		col = self._db['users_strikes']

		strike_info = {
			'user_db_id': db_user['_id'],
			'user_id': bson.Int64(db_user['discord_id']),
			'guild_id': bson.Int64(guild_id),
			'issuer_id': bson.Int64(issuer_id),
			'reason': reason,
			'status': 'active',
			'created_date': datetime.now().isoformat(),
			'updated_date': datetime.now().isoformat()
		}

		result = col.insert_one(strike_info)
		strike_info['_id'] = result.inserted_id

		return strike_info

	def update_strike(self, *, params: dict, query: dict = None, user_id: dict = None) -> Optional[dict]:
		"""
		Update a strike from database
		"""

		col = self._db['users_strikes']

		if query is None and user_id is None:
			raise Exception("query and user_id cannot be None")

		if query is None:
			query = dict()

		if user_id is not None:
			query['user_id'] = user_id

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		for key in params:
			if key == '_id':
				params[key] = ObjectId(params[key])

			elif '_id' in key:
				params[key] = bson.Int64(params[key])

		result = col.find_one_and_update(query, {"$set" : params })

		return result

	def delete_strike(self, *, query: dict = None, user_id: dict = None) -> Optional[dict]:
		"""
		Delete a strike from database.
		"""

		col = self._db['users_strikes']

		if query is None and user_id is None:
			raise Exception("query and user_id cannot be None")

		if query is None:
			query = dict()

		if user_id is not None:
			query['user_id'] = user_id

		for key in query:
			if key == '_id':
				query[key] = ObjectId(query[key])

			elif '_id' in key:
				query[key] = bson.Int64(query[key])

		result = col.find_one_and_delete(query, sort=[('_id', -1)])

		return result