# -*- coding: utf-8 -*-

## Database Module ##
# Connect to database and prepare a connection. #

import logging
from datetime import datetime
from pymongo import MongoClient
import discord, bson
from bson.objectid import ObjectId

log = logging.getLogger(__name__)


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
    log.info(f"Created new connection to database.")

    return _connection


class Database:

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

	# User Timeout related
	def add_user_timeout(self, member, guild, time, issued_by=None, reason=None):
		"""
		Given a user and a time, add a new entry in database

		@member: typeof Discord.Member
		@guild: typeof Discord.Guild
		@time: integer representing time in seconds
		@issued_by: typeof Discord.Member optional: person who issued timeout
		@reason: string Reason of ban

		returns: ban_info
		"""

		col = self._db['users']

		user = col.find_one({'discord_id': member.id})

		if user is None:
			avatar = member.avatar

			if isinstance(member.avatar, discord.asset.Asset):
				avatar = member.avatar.key

			user = {
				'discord_id': bson.Int64(member.id),
				'username': member.name,
				'username_handle': member.discriminator,
				'display_name': member.display_name,
				'avatar': avatar,
				'verified': not member.pending,
				'premium_type': member.premium_since,
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat()
			}

			result = col.insert_one(user)
			user['_id'] = result.inserted_id

		col = self._db['users_bans']
		ban_info = {
			'user_db_id': user['_id'],
			'user_id': bson.Int64(user['discord_id']),
			'guild_id': bson.Int64(guild.id),
			'issuer_id': None,
			'reason': 'No reason specified',
			'time': int(time),
			'status': 'active',
			'created_date': datetime.now().isoformat(),
			'updated_date': datetime.now().isoformat()
		}

		if issued_by is not None:
			ban_info['issuer_id'] = bson.Int64(issued_by.id)

		if reason is not None:
			ban_info['reason'] = reason

		result = col.insert_one(ban_info)
		ban_info['_id'] = result.inserted_id

		return ban_info

	def get_user_timeout(self, member):
		"""
		Given a member, return information about their timeout

		@member: typeof Discord.Member

		returns: ban information
		"""

		col = self._db['users_bans']

		result = col.find_one({'user_id': bson.Int64(member.id), 'status': 'active'})
		if result is None:
			result = dict()

		return result

	def get_user_timeouts(self, member, filter=None):
		"""
		Given a member, return information about their timeout count

		@member: typeof Discord.Member
		@filter: dictionary Additional filters

		returns: list of timeouts
		"""

		col = self._db['users_bans']

		query_filter = {'user_id': bson.Int64(member.id)}

		if filter is not None:
			query_filter.update(filter)

		results = col.find(query_filter)

		return results

	def get_all_timeouts(self, status='active'):
		"""
		Get all current active timeouts

		returns: list of timeouts
		"""

		col = self._db['users_bans']

		results = col.find({'status': status})

		return results

	def remove_user_timeout(self, member):
		"""
		Given a user, suspend his last timeout

		@member: typeof Discord.Member

		returns: integer number of rows updated
		"""

		col = self._db['users_bans']

		member_id = None
		try:
			member_id = member.id
		except:
			member_id = member

		result = col.find_one_and_update({'user_id': bson.Int64(member_id), 'status': 'active'},
			{"$set" : {'status': 'expired', "updated_date": datetime.now().isoformat()} }
		)

		return result

	def update_user_timeout(self, member, params):
		"""
		Given a member, return information about their timeout

		@member: typeof Discord.Member

		returns: ban information
		"""

		col = self._db['users_bans']

		result = col.find_one_and_update({'user_id': bson.Int64(member.id), 'status': 'active'},
			{"$set" : params }
		)
		if result is None:
			result = dict()

		return result

	def add_strike(self, member, guild, issued_by, reason='No reason specified'):
		"""
		Given a member, add a strike to them.

		@member: typeof Discord.Member
		@guild: typeof Discord.Guild
		@issued_by: typeof Discord.Member
		@reason: string

		returns: ban_info
		"""

		col = self._db['users']

		user = col.find_one({'discord_id': bson.Int64(member.id)})

		if user is None:
			avatar = member.avatar

			if isinstance(member.avatar, discord.asset.Asset):
				avatar = member.avatar.key

			user = {
				'discord_id': bson.Int64(member.id),
				'username': member.name,
				'username_handle': member.discriminator,
				'display_name': member.display_name,
				'avatar': avatar,
				'verified': not member.pending,
				'premium_type': member.premium_since,
				'created_date': datetime.now().isoformat(),
				'updated_date': datetime.now().isoformat()
			}

			result = col.insert_one(user)
			user['_id'] = result.inserted_id

		col = self._db['users_strikes']

		strike_info = {
			'user_db_id': user['_id'],
			'user_id': bson.Int64(user['discord_id']),
			'guild_id': bson.Int64(guild.id),
			'issuer_id': bson.Int64(issued_by.id),
			'reason': reason,
			'status': 'active',
			'created_date': datetime.now().isoformat(),
			'updated_date': datetime.now().isoformat()
		}

		result = col.insert_one(strike_info)
		strike_info['_id'] = result.inserted_id

		return strike_info

	def remove_strike(self, member, guild, strike_id):
		"""
		Given a member, remove a strike from them.

		@member: typeof Discord.Member
		@guild: typeof Discord.Guild
		@issued_by: typeof Discord.Member
		@reason: string

		returns: ban_info
		"""

		col = self._db['users_strikes']

		result = col.find_one_and_update({'_id': ObjectId(strike_id), 'user_id': bson.Int64(member.id), 'status': 'active'},
			{"$set" : {'status': 'expired', "updated_date": datetime.now().isoformat()} }
		)

		return result

	def delete_strike(self, member, guild):
		"""
		Given a member, delete a strike from them.

		@member: typeof Discord.Member
		@guild: typeof Discord.Guild

		returns: ban_info
		"""

		col = self._db['users_strikes']

		result = col.find_one_and_delete({'user_id': bson.Int64(member.id), 'guild_id': bson.Int64(guild.id), 'status': 'active'}, sort=[('_id', -1)])

		return result

	def get_user_strikes(self, member):
		"""
		Given a member get all striked timeouts

		@member: typeof Discord.Member

		returns: list of striked timeouts
		"""

		col = self._db['users_strikes']

		results = col.find({'user_id': bson.Int64(member.id), 'status': 'active'})

		return results

	def get_all_user_strikes(self, member):
		"""
		Given a member get all striked timeouts

		@member: typeof Discord.Member

		returns: list of striked timeouts
		"""

		col = self._db['users_strikes']

		results = col.find({'user_id': bson.Int64(member.id)})

		return results

	# Server Configuration Related
	def load_server_configuration(self, guild, bot):
		"""
		Given a guild, load its configuration

		@guild: typeof Discord.Guild

		returns: guild_config
		"""

		col = self._db['discord_config']

		guild_info = col.find_one({'guild_id': bson.Int64(guild.id)})

		if guild_info is None:

			# Get default admin roles
			admin_roles = []

			for role in guild.roles:
				if role.permissions.administrator:
					admin_roles.append(bson.Int64(role.id))

			guild_info = {
				'guild_id': bson.Int64(guild.id),
				'name': guild.name,
				'command_character': bot.config['discord']['default_command_character'],
				'modmail_character': bot.config['modmail']['default_command_character'],
				'allowed_channels': list(),
				'denied_channels': list(),
				'admin_roles': admin_roles,
				'mod_roles': list(),
				'ban_roles': list(),
				'log_channel': None,
				'modmail_channel': None,
				'override_silent': False,
				'auto_timeout_on_reenter': True,
				'joined_date': datetime.now().isoformat()
			}

			result = col.insert_one(guild_info)
			guild_info['_id'] = result.inserted_id

		return guild_info

	def update_server_configuration(self, guild, parameters):
		"""
		Given a guild, update its configuration

		@guild: typeof Discord.Guild
		@parameters: dictionary with values to update

		returns: guild_config
		"""

		col = self._db['discord_config']

		guild_info = col.find_one_and_update({'guild_id': bson.Int64(guild.id)}, {"$set": parameters })

		return guild_info

	def add_role_to_guild(self, guild, list_name, parameter):
		"""
		Given a guild, add one of its list configuration

		@guild: typeof Discord.Guild
		@list_name: string list name to be updated
		@parameter: typeof(any) value to be added

		returns: guild_config
		"""

		col = self._db['discord_config']

		guild_info = col.find_one_and_update({'guild_id': bson.Int64(guild.id)}, {"$push": {list_name: parameter} })

		return guild_info

	def remove_role_from_guild(self, guild, list_name, parameter):
		"""
		Given a guild, remove one of its list configuration

		@guild: typeof Discord.Guild
		@list_name: string list name to be updated
		@parameter: typeof(any) value to be added

		returns: guild_config
		"""

		col = self._db['discord_config']

		guild_info = col.find_one_and_update({'guild_id': bson.Int64(guild.id)}, {"$pull": {list_name: parameter} })

		return guild_info

	def get_banwords(self, query=None):
		"""
		Return all banwords associated with it

		returns: list of Banword
		"""

		col = self._db['banwords']

		params = {}

		if query is not None:
			params.update(query)

		results = col.find(params)

		return list(results)


if __name__ == '__main__':
	import pprint

	config = {
		'path': 'mongodb://sakurazaki:testpasswd@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false',
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
		'created_date': datetime.now().isoformat(),
		'updated_date': datetime.now().isoformat()
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
