
## Database Module ##
# Connect to database and prepare a connection. #

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from bson.objectid import ObjectId

log: logging.Logger = logging.getLogger("database")


class PitBotDatabase:
    def __init__(self, *, database):
        self._db = database._db

    def close(self):
        self._db.close()

    # Timeouts
    def get_timeout(self, query: dict, partial: bool = True) -> dict[str, Any] | None:
        """
        Return information about a single timeout.
        In the case of being multiple it will always return the first.
        """
        col = self._db['users_timeouts']
        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])
        result = col.find_one(query)

        if not partial:
            col = self._db['users']
            result['issuer'] = col.find_one({'discord_id': result['issuer_id']})
        return result

    def get_timeouts(self, query: dict, sort: tuple[str, int] | None = None, partial: bool = True) -> list[dict[str, Any]]:
        """Return information about timeout(s)"""
        col = self._db['users_timeouts']
        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])

        results = col.find(query)
        if sort:
            results = results.sort(sort[0], sort[1])
        results = list(results)

        if not partial:
            col = self._db['users']
            for timeout in results:
                # Include issuer in information
                # Potentially also add guild
                timeout['user'] = col.find_one({'discord_id': timeout['user_id']})
                timeout['issuer'] = col.find_one({'discord_id': timeout['issuer_id']})
        return results

    def create_timeout(self, user: "discord.User", guild_id: str, time: int, 
        issuer_id: str = None, reason: str | None = None, source: str | None = 'command') -> dict[str, Any]:
        """Create a new timeout in the database."""
        col = self._db['users']
        db_user = col.find_one({'discord_id': str(user.id)})
        if db_user is None:
            db_user = {
                'discord_id': str(user.id),
                'username': user.name,
                'discriminator': user.discriminator,
                'created_date': datetime.now().isoformat(),
                'updated_date': datetime.now().isoformat()
            }
            result = col.insert_one(db_user)
            db_user['_id'] = result.inserted_id

        col = self._db['users_timeouts']
        timeout_info = {
            'user_db_id': db_user['_id'],
            'user_id': db_user['discord_id'],
            'guild_id': str(guild_id),
            'issuer_id': None,
            'reason': 'No reason specified',
            'time': int(time),
            'status': 'active',
            'created_date': datetime.now().isoformat(),
            'updated_date': datetime.now().isoformat(),
            'source': source
        }

        if issuer_id is not None:
            timeout_info['issuer_id'] = str(issuer_id)

        if reason is not None:
            timeout_info['reason'] = reason

        result = col.insert_one(timeout_info)
        timeout_info['_id'] = result.inserted_id

        return timeout_info

    def update_timeout(self, *, params: dict, query: dict = None, user_id: str = None) -> dict[str, Any] | None:
        """Update a timeout from database."""
        col = self._db['users_timeouts']

        if query is None and user_id is None:
            raise Exception("query and user_id cannot be None")

        if query is None:
            query = {}

        if user_id is not None:
            query['user_id'] = user_id

        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])
        if params.get("_id"):
            params['_id'] = ObjectId(params['_id'])

        result = col.find_one_and_update(query, {"$set" : params })

        return result

    def delete_timeout(self, *, query: dict = None, user_id: str = None) -> dict[str, Any] | None:
        """Delete a timeout from database."""
        col = self._db['users_timeouts']

        if query is None and user_id is None:
            raise Exception("query and user_id cannot be None")

        if query is None:
            query = {}

        if user_id is not None:
            query['user_id'] = str(user_id)

        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])

        result = col.find_one_and_delete(query, sort=[('_id', -1)])

        return result

    # Strikes
    def get_strikes(self, query: dict, sort: tuple[str, int] | None = None, partial: bool = True) -> list[dict[str, Any]]:
        """Return information about timeout(s)"""
        col = self._db['users_strikes']

        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])

        results = col.find(query)

        if sort:
            results = results.sort(sort[0], sort[1])

        results = list(results)

        if not partial:
            col = self._db['users']

            for strike in results:
                # Include issuer in information
                # Potentially also add guild
                strike['user'] = col.find_one({'discord_id': strike['user_id']})
                strike['issuer'] = col.find_one({'discord_id': strike['issuer_id']})

        return results

    def create_strike(self, user: "discord.User", guild_id: str, issuer_id: str,
            reason: str = 'No reason specified') -> dict[str, Any]:
        """Given a member, add a strike to them."""
        col = self._db['users']

        db_user = col.find_one({'discord_id': str(user.id)})

        if db_user is None:
            db_user = {
                'discord_id': str(user.id),
                'username': user.name,
                'discriminator': user.discriminator,
                'created_date': datetime.now().isoformat(),
                'updated_date': datetime.now().isoformat()
            }

            result = col.insert_one(db_user)
            db_user['_id'] = result.inserted_id

        col = self._db['users_strikes']

        strike_info = {
            'user_db_id': db_user['_id'],
            'user_id': db_user['discord_id'],
            'guild_id': str(guild_id),
            'issuer_id': str(issuer_id),
            'reason': reason,
            'status': 'active',
            'created_date': datetime.now().isoformat(),
            'updated_date': datetime.now().isoformat()
        }

        result = col.insert_one(strike_info)
        strike_info['_id'] = result.inserted_id

        return strike_info

    def update_strike(self, *, params: dict, query: dict = None, user_id: str = None) -> dict[str, Any] | None:
        """Update a strike from database"""
        col = self._db['users_strikes']

        if query is None and user_id is None:
            raise Exception("query and user_id cannot be None")

        if query is None:
            query = {}

        if user_id is not None:
            query['user_id'] = str(user_id)

        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])
        if params.get("_id"):
            params['_id'] = ObjectId(params['_id'])

        params['updated_date'] = datetime.now()

        result = col.find_one_and_update(query, {"$set" : params })

        return result

    def delete_strike(self, *, query: dict = None, user_id: str = None) -> dict[str, Any] | None:
        """Delete a strike from database."""
        col = self._db['users_strikes']

        if query is None and user_id is None:
            raise Exception("query and user_id cannot be None")

        if query is None:
            query = {}

        if user_id is not None:
            query['user_id'] = str(user_id)

        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])

        result = col.find_one_and_delete(query, sort=[('_id', -1)])

        return result

    # Users
    def get_user(self, query: dict) -> dict[str, Any] | None:
        """Get a user from database."""
        col = self._db['users']
        user = col.find_one(query)
        return user
