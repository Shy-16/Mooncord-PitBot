# -*- coding: utf-8 -*-

## Database Module ##
# Connect to database and prepare a connection. #

import logging
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import Optional

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

    # Server Configuration Related
    def get_default_guild(self) -> dict:
        """
        Loads the first guild in the list from database
        """

        col = self._db['discord_config']

        guild_info = col.find_one()

        return guild_info

    async def load_server_configuration(self, guild, bot) -> dict:
        """
        Given a guild, load its configuration
        """

        col = self._db['discord_config']

        guild_info = col.find_one({'guild_id': guild.id})

        if guild_info is None:
            # guild info has the following attrs
            # 'features', 'icon', 'id', 'name', 'owner', 'permissions'

            # Get guild info from discord
            dc_guild = await bot.http.get_guild(guild.id)

            # Get default admin roles
            admin_roles = []

            # roles
            # {'id': '553455586709078024', 'name': 'Bots', 'permissions': '6546775617', 'position': 2, 'color': 0, 
            # 'hoist': True, 'managed': False, 'mentionable': False, 'icon': None, 'unicode_emoji': None}

            for role in dc_guild['roles']:
                # 1 << 3 == 0x8 == administrator
                if (int(role['permissions']) & 1 << 3) == 0x8 and not "tags" in role:
                    admin_roles.append(role['id'])

            guild_info = {
                'guild_id': guild.id,
                'name': guild.name,
                'command_character': bot.config['discord']['default_command_character'],
                'modmail_character': bot.config['discord']['default_command_character'],
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

        guild_info = col.find_one_and_update({'guild_id': guild.id}, {"$set": parameters })

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

        guild_info = col.find_one_and_update({'guild_id': guild.id}, {"$push": {list_name: parameter} })

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

        guild_info = col.find_one_and_update({'guild_id': guild.id}, {"$pull": {list_name: parameter} })

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

    def store_roles(self, user: dict, guild_id: str) -> Optional[dict]:
        """
        Store roles for a user who is marked to be pruned
        """

        col = self._db['prune_users']

        user_info = {
            'user_id': user['user']['id'],
            'guild_id': guild_id,
            'roles': user['roles'],
            'created_date': datetime.now().isoformat()
        }

        result = col.insert_one(user_info)
        user_info['_id'] = result.inserted_id

        return user_info

    def get_stored_roles(self, user_id: str, guild_id: str) -> Optional[dict]:
        """
        Given a user and a guild check if there are roles stored and return them
        """

        col = self._db['prune_users']

        params = {
            'user_id': user_id,
            'guild_id': guild_id
        }

        result = col.find_one(params)

        return result

    def delete_stored_roles(self, user_id: str, guild_id: str) -> Optional[dict]:
        """
        Given a user and a guild check if there are roles stored and delete them
        """

        col = self._db['prune_users']

        params = {
            'user_id': user_id,
            'guild_id': guild_id
        }

        result = col.find_one_and_delete(params)

        return result


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
    results = col.find({'user_id': "539881999926689829"})

    for res in results:
        pprint.pprint(res)

    col = db['users']
    col.find_one_and_delete({'discord_id': 5549})

    conn.close()
