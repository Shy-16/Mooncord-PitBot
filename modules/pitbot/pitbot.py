# -*- coding: utf-8 -*-

## Pitbot Module ##
# Takes care of timing out and releasing people #

from __future__ import annotations

import logging
import datetime
from typing import Any

import discord

from modules.context import CommandContext, DMContext, InteractionContext
from .database import PitBotDatabase
from .commands import Timeout, BotConfig, Release, Roles, Shutdown

log: logging.Logger = logging.getLogger("pitbot")


class PitBot:
    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot = bot
        self._db = PitBotDatabase(database=bot.db)

        self.commands = {
            "shutdown": Shutdown(self, 'admin'),
            "config": BotConfig(self, 'admin'),
            "timeout": Timeout(self, 'mod', ['ban', 'time', 'remaining', 'timeout']),
            "timeoutns": Timeout(self, 'mod', skip_strike=True),
            "release": Release(self, 'mod'),
            "roles": Roles(self, 'mod'),
        }

        self.dm_commands = {
            "timeout": self.commands['timeout']
        }

        self.ping_commands = {
            "timeout": self.commands['timeout']
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

    async def handle_ping_commands(self, message: discord.Message) -> None:
        """Handles any commands given by a user through a ping"""
        command = message.content
        params = message.content.split()

        # We need to make sure that whoever pinged the bot used @sayo as first positional argument
        if len(params) <= 1:
            # we dont care about people just pinging the bot
            return
        
        if params[0] != f'<@{self._bot.user.id}>':
            # we dont care about people pinging the bot as part of the message
            return

        command = params[1].lower()
        params = params[2:]

        if command in self.ping_commands:
            await self.ping_commands[command].ping(CommandContext(self._bot, command, params, message))
        return

    # Functionality

    # Timeouts related
    def get_user_timeout(self, user: discord.User, partial: bool = True) -> dict[str, Any] | None:
        """Gets a timeout for a user. If no active timeouts are found returns None"""
        query = {'user_id': str(user.id), 'status': 'active'}
        timeout = self._db.get_timeout(query, partial)
        return timeout

    def get_user_timeouts(self, user: discord.User, sort: tuple[str, int] | None = None, 
                            status: str | None = None, partial: bool = True) -> list[dict[str, Any]]:
        """
        Gets a list of timeouts for a user.

        Status is used to filter.
        """
        query = {'user_id': str(user.id)}
        if status:
            query['status'] = status
        timeouts = self._db.get_timeouts(query, sort, partial)
        return timeouts

    def add_timeout(self, *, user: discord.User, guild_id: int, time: int, issuer_id: int,
        reason: str = 'No reason specified.', source: str = 'command') -> dict[str, Any] | None:
        """Adds a timeout to a user"""
        timeout = self._db.create_timeout(user, guild_id, time, issuer_id, reason, source)
        return timeout

    def extend_timeout(self, *, user: discord.User, time: int) -> dict[str, Any] | None:
        """Extends the duration of an active timeout by specified amount"""
        params = {'time': time}
        query = {'user_id': str(user.id), 'status': 'active'}
        timeout = self._db.update_timeout(params=params, query=query)
        return timeout

    def expire_timeout(self, *, user: discord.User) -> dict[str, Any] | None:
        """Sets a timeout as expired"""
        params = {'status': 'expired', 'updated_date': datetime.datetime.now().isoformat()}
        query = {'user_id': str(user.id), 'status': 'active'}
        timeout = self._db.update_timeout(params=params, query=query)
        return timeout

    def delete_timeout(self, *, user: discord.User) -> dict[str, Any] | None:
        """Deletes a timeout from database"""
        query = {'user_id': str(user.id), 'status': 'active'}
        timeout = self._db.delete_timeout(query=query)
        return timeout

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
        
        description = "Pit module takes of timing out or releasing users and adding strikes to their history."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'timeout', 'value': f"{context.command_character}timeout will set a timeout for a given user.\r\n"+ 
                "The time parameter expects the following format: <1-2 digit number><one of: s, m, h, d> where s is second, m is minute, h is hour, d is day.\r\n\r\n"+
                f"Example command: {context.command_character}timeout <@{self._bot.user.id}> 24h Being a bad bot", 'inline': False},
            {'name': 'timeoutns', 'value': f"{context.command_character}timeoutns will set a timeout for a given user without adding a strike to their account.\r\n"+ 
                f"Usage is the same as `{context.command_character}timeout`", 'inline': False},
            {'name': 'release', 'value': f"{context.command_character}release will end a user's timeout immediately.\r\n"+ 
                "Optional parameter: `amend`: If amend is provided it will also delete the most recent strike issued to the user.\r\n\r\n"+
                f"Example command: {context.command_character}release <@{self._bot.user.id}> amend", 'inline': False},
        ]
        return {
            "title": "Pit Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
