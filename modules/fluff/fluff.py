# -*- coding: utf-8 -*-

## Stickers Module ##
# Shows different stats for sticker usage #

import logging
from typing import Any

import discord

from modules.context import CommandContext
from .commands import ExecuteCommand

log: logging.Logger = logging.getLogger("fluff")


class Fluff:
    def __init__(self, *, bot: discord.Client) -> None:
        self._bot = bot

        self.commands = {
        }

        self.ping_commands = {
            "execute": ExecuteCommand(self, 'mod'),
        }

    def init_tasks(self) -> None:
        """Initialize the different asks that run in the background"""

    async def handle_commands(self, message: str) -> None:
        """Handles any commands given through the designed character"""
        
        command = message.content.replace(self._bot.guild_config[message.guild.id]['command_character'], '')
        params = []

        if ' ' in command:
            command, params = (command.split()[0], command.split()[1:])

        command = command.lower()
        
        if command in self.commands:
            await self.commands[command].execute(CommandContext(self._bot, command, params, message))
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

    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Fluff module adds commands that do literally nothing. They are just for fun."
        fields = [
            {'name': 'moon2DOIT', 'value': f"<@{self._bot.user.id}> execute order 66.\r\n", 'inline': False},
        ]
        return {
            "title": "Fluff Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }