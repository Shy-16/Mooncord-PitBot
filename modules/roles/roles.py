# -*- coding: utf-8 -*-

## Roles Module ##
# Assigns or removes role in batch #

from __future__ import annotations

import logging
from typing import Any

import discord

from modules.context import CommandContext, InteractionContext
from .commands import RolesCommand

log: logging.Logger = logging.getLogger("roles")


class Roles:
    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot = bot

        self.commands = {
            "roles": RolesCommand(self, 'mod'),
        }

        self.dm_commands = {
        }

        self.ping_commands = {
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

    # Module help
    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Pit module takes of timing out or releasing users and adding strikes to their history."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'roles', 'value': f"{context.command_character}roles will take a list of roles and users and either \
                add or remove all given roles in the list to all given users.\r\n"+ 
                "This comand has additional help information within the command.\r\n"+
                f"Example command: {context.command_character}roles add @GAMEJAM @GAMEDEV <@{self._bot.user.id}>.", 'inline': False},
        ]
        return {
            "title": "Roles Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
