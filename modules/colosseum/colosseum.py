# -*- coding: utf-8 -*-

## Pitbot Module ##
# Takes care of timing out and releasing people #

from __future__ import annotations

import logging
import datetime
from typing import Any

import discord

from modules.context import CommandContext, InteractionContext
from .database import ColosseumDatabase

log: logging.Logger = logging.getLogger("pitbot")


class Colosseum:
    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot = bot
        self._db = ColosseumDatabase(database=bot.db)

        self.commands = {}
        self.dm_commands = {}
        self.ping_commands = {}

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

    async def handle_ping_commands(self, message: discord.Message) -> None:
        """Handles any commands given by a user through a ping"""

    # Colosseum
    def create_user(self, user: discord.Member) -> dict[str, Any]:
        """Creates a new user in the Colosseum"""
        return self._db.create_user(user)
        
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
    
    def create_duel(self, user: discord.Member, target: discord.Member) -> dict[str, Any]:
        """Creates a duel in database"""
        return self._db.create_duel(user, target)
    
    def get_duel(self, *, user: discord.Member | None) -> dict[str, Any]:
        """Gets a duel between 2 users"""
        query = {'discord_id': str(user.id)}
        return self._db.create_user(query)

    # Module help
    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Colosseum is a server-wide event where you can duel members to earn loot and money."
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
            "title": "Colosseum Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
