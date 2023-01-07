
## Database Module ##
# Handle Module related database queries. #

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from bson.objectid import ObjectId

log: logging.Logger = logging.getLogger("database")


class WatchListDatabase:
    def __init__(self, *, database):
        self._db = database._db

    def close(self):
        self._db.close()

    # Timeouts
    def get_watchlist(self, query: dict, sort: tuple[str, int] | None = None, partial: bool = True) -> list[dict[str, Any]]:
        """Return information about all watchlist"""
        col = self._db['watchlist']
        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])

        results = col.find(query)
        if sort:
            results = results.sort(sort[0], sort[1])
        results = list(results)

        if not partial:
            col = self._db['users']
            for entry in results:
                entry['user'] = col.find_one({'discord_id': entry['user_id']})
                entry['issuer'] = col.find_one({'discord_id': entry['issuer_id']})
        return results
    
    def get_watchlist_entry(self, query: dict, partial: bool = True) -> dict[str, Any] | None:
        """Return information about one entry"""
        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])
            
        col = self._db['watchlist']
        entry = col.find_onefind_one(query)
        if not partial:
            col = self._db['users']
            entry['user'] = col.find_one({'discord_id': entry['user_id']})
            entry['issuer'] = col.find_one({'discord_id': entry['issuer_id']})
        return entry

    def create_watchlist_entry(self, user: "discord.User", guild_id: str, issuer_id: str = None, 
            reason: str | None = None) -> dict[str, Any]:
        """Create a new entry in watchlist."""
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
        col = self._db['watchlist']
        entry_info = {
            'user_db_id': db_user['_id'],
            'user_id': db_user['discord_id'],
            'guild_id': str(guild_id),
            'issuer_id': None,
            'reason': 'No reason specified',
            'status': 'active',
            'created_date': datetime.now().isoformat(),
            'updated_date': datetime.now().isoformat()
        }
        if issuer_id is not None:
            entry_info['issuer_id'] = str(issuer_id)
        if reason is not None:
            entry_info['reason'] = reason
        result = col.insert_one(entry_info)
        entry_info['_id'] = result.inserted_id
        return entry_info

    def delete_watchlist_entry(self, *, query: dict = None, user_id: str = None) -> dict[str, Any] | None:
        """Delete a watchlist entry."""
        col = self._db['watchlist']
        if query is None and user_id is None:
            raise Exception("query and user_id cannot be None")
        if query is None:
            query = {}
        if user_id is not None:
            query['user_id'] = str(user_id)
        if query.get("_id"):
            query['_id'] = ObjectId(query['_id'])
        result = col.find_one_and_delete(query)
        return result

    def get_user(self, query: dict) -> dict[str, Any] | None:
        """Get a user from database."""
        col = self._db['users']
        user = col.find_one(query)
        return user