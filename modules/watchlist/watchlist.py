# -*- coding: utf-8 -*-

## WatchList Module ##
# Adds and removes users to the watchlist #

from __future__ import annotations

import logging
from typing import Any

import discord

from modules.context import CommandContext, InteractionContext
from .database import WatchListDatabase
from .commands import WatchListCommand, Watch, UnWatch

log: logging.Logger = logging.getLogger("watchlist")


class WatchList:
    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot = bot
        self._db = WatchListDatabase(database=bot.db)

        self.commands = {
            "watchlist": WatchListCommand(self, 'mod'),
            "watch": Watch(self, 'mod'),
            "unwatch": UnWatch(self, 'mod'),
        }

        self.commands['wl'] = self.commands['watchlist']
        self.commands['wa'] = self.commands['watch']
        self.commands['wr'] = self.commands['unwatch']
        self.commands['uw'] = self.commands['unwatch']

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

    # Functionality
    def get_watchlist(self, sort: tuple[str, int] | None = None, status: str | None = None, 
            partial: bool = True) -> list[dict[str, Any]]:
        """Gets watchlist."""
        query = {}
        if status:
            query['status'] = status
        entries = self._db.get_watchlist(query, sort, partial)
        return entries

    def create_watchlist_entry(self, *, user: discord.User, guild_id: int, issuer_id: int,
            reason: str = 'No reason specified.') -> dict[str, Any] | None:
        """Adds a timeout to a user"""
        query = {'user_id': str(user.id), 'status': 'active'}
        entry = self._db.get_watchlist_entry(query)
        if entry is None:
            entry = self._db.create_watchlist_entry(user, guild_id, issuer_id, reason)
        return entry

    def delete_watchlist_entry(self, *, user: discord.User) -> dict[str, Any] | None:
        """Deletes a timeout from database"""
        query = {'user_id': str(user.id), 'status': 'active'}
        entry = self._db.delete_watchlist_entry(query=query)
        return entry

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

    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Pit module takes of timing out or releasing users and adding strikes to their history."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'watchlist | wl', 'value': f"{context.command_character}wl will show all watchlist.\r\n\r\n"+ 
                f"Example command: {context.command_character}wl", 'inline': False},
            {'name': 'watch | wa', 'value': f"{context.command_character}wa will add a user to watchlist.\r\n\r\n"+ 
                f"Example command: {context.command_character}wa <@{self._bot.user.id}>", 'inline': False},
            {'name': 'unwatch | uw | wr', 'value': f"{context.command_character}uw will remove a user from watchlist.\r\n\r\n"+ 
                f"Example command: {context.command_character}uw <@{self._bot.user.id}>", 'inline': False},
        ]
        return {
            "title": "Pit Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
