
## Database Module ##
# Connect to database and prepare a connection. #

from __future__ import annotations

import logging
import datetime
from typing import Any

import discord
from bson.objectid import ObjectId

log: logging.Logger = logging.getLogger("database")


class ColosseumDatabase:
    def __init__(self, *, database):
        self._db = database._db

    def close(self):
        self._db.close()

    # Colosseum

    # Users
    def create_user(self, user: discord.Member) -> dict[str, Any]:
        """Create a new user for the Colosseum"""
        col = self._db['colosseum_user']
        db_user = col.find_one({'discord_id': str(user.id)})
        if db_user is None:
            db_user = {
                'discord_id': str(user.id),
                'username': user.name,
                'discriminator': user.discriminator,
                'victories': 0,
                'loses': 0,
                'reputation': 1000,
                'money': 0,
                'gear': {
                    'head': None,
                    'torso': None,
                    'legs': None,
                    'feet': None,
                    'amulet': None,
                    'ring': None
                },
                'created_date': datetime.datetime.now().isoformat(),
                'updated_date': datetime.datetime.now().isoformat(),
            }
            result = col.insert_one(db_user)
            db_user['_id'] = result.inserted_id
        return db_user
        
    def get_user(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Get a user from database."""
        col = self._db['colosseum_user']
        user = col.find_one(query)
        return user

    # Duel
    def create_duel(self, user: discord.Member, target: discord.Member) -> dict[str, Any]:
        """Create a new user for the Colosseum"""
        col = self._db['colosseum_user']
        db_user = col.find_one({'discord_id': str(user.id)})
        if db_user is None:
            db_user = {
                'requester_id': str(user.id),
                'target_id': str(target.id),
                'bet': 0,
                'created_date': datetime.datetime.now().isoformat(),
            }
            result = col.insert_one(db_user)
            db_user['_id'] = result.inserted_id
        return db_user
    
    def get_duel(self, query: dict[str, Any]) -> dict[str, Any] | None:
        col = self._db['colosseum_duel']
        duel = col.find_one(query)
        if duel is not None:
            duel['requester'] = self.get_user({'discord_id': duel['requester_id']})
            duel['target'] = self.get_user({'discord_id': duel['target_id']})
        return duel
