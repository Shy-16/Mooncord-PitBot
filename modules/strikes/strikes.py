# -*- coding: utf-8 -*-

## Strikes Module ##
# This module will take care of strikes for users #

from __future__ import annotations

import logging
import datetime
from typing import Any

import discord

from modules.context import CommandContext, DMContext, InteractionContext
from modules.pitbot.database import PitBotDatabase
from .commands import Strike

log: logging.Logger = logging.getLogger("strikes")


class Strikes:
    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot = bot
        self._db = PitBotDatabase(database=bot.db)

        self.commands = {
            "strikes": Strike(self, 'mod', ['strikes', 'pithistory', 'history'])
        }

        self.dm_commands = {
            "strikes": self.commands['strikes'],
        }

    def init_tasks(self) -> None:
        """Initialize the different asks that run in the background"""

    async def handle_commands(self, message: discord.Message) -> None:
        """Handles any commands given through the designed character"""
        command = message.content.replace(self._bot.guild_config[message.guild.id]['command_character'], '')
        params = []
        if ' ' in command:
            command, params = (command.split()[0], command.split()[1:])
        command = command.lower()
        if command in self.commands:
            await self.commands[command].execute(CommandContext(self._bot, command, params, message))
        return

    async def handle_dm_commands(self, message: discord.Message) -> None:
        """Handles any commands given by a user through DMs"""
        for _, dm_command in self.dm_commands.items():
            for keyword in dm_command.dm_keywords:
                if keyword in message.content:
                    await dm_command.dm(DMContext(self._bot, message))
                    return
        return

    # Strikes related
    def get_user_strikes(self, user: discord.User, sort: tuple[str, int] | None = None, 
                            status: str | None = None, partial: bool = True) -> list[dict[str, Any]]:
        """
        Gets all strikes of a user.

        If partial is false full information of strike will be sent.
        Including information about users.
        """
        query = {'user_id': str(user.id)}
        if status:
            query['status'] = status
        strikes = self._db.get_strikes(query, sort, partial)
        return strikes

    def add_strike(self, *, user: discord.User, guild_id: int, issuer_id: int,
        reason: str = 'No reason specified.') -> dict[str, Any] | None:
        """Adds a strike to a user."""
        strike = self._db.create_strike(user, guild_id, issuer_id, reason)
        return strike

    def expire_strike(self, *, user: discord.User, strike_id: int) -> dict[str, Any] | None:
        """Sets a strike as expired"""
        if strike_id == "oldest":
            # Get all active strikes, sort them by ID, get the ID of the latest
            strikes = self._db.get_strikes({'user_id': str(user.id), 'status': 'active'})
            if len(strikes) <= 0:
                return None
            strike_id = str(strikes[0]['_id'])
        params = {'status': 'expired', 'updated_date': datetime.datetime.now().isoformat()}
        query = {'_id': strike_id, 'user_id': str(user.id), 'status': 'active'}
        strike = self._db.update_strike(params=params, query=query)
        return strike

    def delete_strike(self, *, user: discord.User, strike_id: int = 'newest') -> dict[str, Any] | None:
        """Deletes a strike from database"""
        if strike_id == "newest":
            # Get all active strikes, sort them by ID, get the ID of the newest
            strikes = self._db.get_strikes({'user_id': str(user.id), 'status': 'active'}, ('_id', -1))
            if len(strikes) <= 0:
                return None
            strike_id = str(strikes[0]['_id'])
        query = {'_id': strike_id, 'user_id': str(user.id), 'status': 'active'}
        strike = self._db.delete_strike(query=query)
        return strike

    # Users related
    def get_user(self, *, user_id: str | None = None, username: dict[str, Any] | None = None,
        discriminator: str | None = None) -> dict[str, Any] | None:
        """Get a user from database."""
        if user_id is not None:
            query = {'discord_id': str(user_id)}
        elif username is not None and discriminator is not None:
            query = {'username': username, 'discriminator': discriminator}
        else:
            raise Exception("user_id or username and discriminator cannot be None.")
        user = self._db.get_user(query)
        if user:
            user['id'] = user['discord_id']
        return user

    # Module help
    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Strikes module allows for user strikes management."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'List', 'value': f"{context.command_character}strikes @user <verbose:optional> to get all strikes a user has.", 'inline': False},
            {'name': 'Add', 'value': f"{context.command_character}strikes @user add <reason:optional> to add a strike.", 'inline': False},
            {'name': 'Expire', 'value': f"{context.command_character}strikes @user exp|expire <strike_id>|oldest to set a strike as expired.", 'inline': False},
            {'name': 'Delete', 'value': f"{context.command_character}strikes @user del|delete <strike_id>|newest to remove a strike from a user.", 'inline': False},
            {'name': 'Keywords', 'value': "<strike_id> is the UniqueID provided on the list of strikes of the user, which uniquely identify each strike.\r\n" \
            "`oldest` will get the oldest strike by date. `newest` will get the newest strike by date.", 'inline': False},
            {'name': 'Example', 'value': f"{context.command_character}strikes <@{self._bot.user.id}> add Too dumb.", 'inline': False}
        ]
        return {
            "title": "Strikes Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
