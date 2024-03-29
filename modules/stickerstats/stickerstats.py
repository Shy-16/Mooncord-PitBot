# -*- coding: utf-8 -*-

## Stickers Module ##
# Shows different stats for sticker usage #

import logging
from typing import Any

import discord

from modules.context import CommandContext, InteractionContext
from .database import StickerDatabase
from .commands import StickerCommand

log: logging.Logger = logging.getLogger("sticker")


class StickerStats:

    def __init__(self, *, bot: discord.Client) -> None:
        """
        :var bot discord.Client: The bot instance
        """

        self._bot = bot
        self._db = StickerDatabase(database=bot.db)

        self.commands = {
            "sticker": StickerCommand(self, 'mod'),
        }

    def init_tasks(self) -> None:
        """
        Initialize the different asks that run in the background
        """
        pass

    async def handle_commands(self, message: str) -> None:
        """
        Handles any commands given through the designed character
        """
        
        command = message.content.replace(self._bot.guild_config[message.guild.id]['command_character'], '')
        params = list()

        if ' ' in command:
            command, params = (command.split()[0], command.split()[1:])

        command = command.lower()
        
        if command in self.commands:
            await self.commands[command].execute(CommandContext(self._bot, command, params, message))
        return

    # Functionality
    def get_sticker(self, *, sticker_id: str = None, name: str = None) -> dict:
        """
        Gets a sticker from database given either id or name
        """

        query = dict()

        if sticker_id is not None:
            query['id'] = str(sticker_id)

        if name is not None:
            query['name'] = name

        sticker = self._db.get_sticker(query)

        return sticker

    def update_sticker(self, *, message: discord.Message) -> None:
        """Updates info about sticker(s)"""

        for sticker in message.stickers:
            sticker_info = self._db.get_sticker({'id': str(sticker.id)})

            if not sticker_info:
                self._db.create_sticker(sticker, channel_id=str(message.channel.id))

            else:
                self._db.update_sticker_stats(sticker=sticker_info, channel_id=str(message.channel.id))

    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Sticker module reads stickers used in mooncord and gather usage stats for them."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'sticker', 'value': f"{context.command_character}sticker will display stats for given sticker.\r\n"+ 
                "The sticker can be given with the exact name or can be attached as a sticker.\r\n\r\n"+
                f"Example command: {context.command_character}sticker STARE", 'inline': False},
        ]
        return {
            "title": "Sticker Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
