# -*- coding: utf-8 -*-

## Config Module ##
# General bot configuration #

import logging
from typing import Any

import discord

from modules.context import CommandContext, InteractionContext
from .commands import BotConfig, Shutdown

log: logging.Logger = logging.getLogger("config")


class Config:

    def __init__(self, *, bot: discord.Client) -> None:
        """:var bot discord.Client: The bot instance"""
        self._bot = bot

        self.commands = {
            "config": BotConfig(self, 'admin'),
            "shutdown": Shutdown(self, 'admin'),
        }

    def init_tasks(self) -> None:
        """Initialize the different asks that run in the background"""

    async def handle_commands(self, message: str) -> None:
        """Handles any commands given through the designed character"""
        
        command = message.content.replace(self._bot.guild_config[message.guild.id]['command_character'], '')
        params = list()

        if ' ' in command:
            command, params = (command.split()[0], command.split()[1:])

        command = command.lower()
        
        if command in self.commands:
            await self.commands[command].execute(CommandContext(self._bot, command, params, message))
        return

    # Functionality
    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Sticker module reads stickers used in mooncord and gather usage stats for them."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'config', 'value': f"{context.command_character}config will show server configuration.\r\n"+
                "You can configure server variables with this command.", 'inline': False},
            {'name': 'shutdown', 'value': "Shut down the bot (Warning: This doesn't restart it) - Admin only command.\r\n"+ 
                f"Example command: {context.command_character}shutdown", 'inline': False}
        ]
        return {
            "title": "Config Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
