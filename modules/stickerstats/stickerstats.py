# -*- coding: utf-8 -*-

## Stickers Module ##
# Shows different stats for sticker usage #

import logging
import datetime
from typing import Optional, List, Union, Tuple

import discord

from modules.context import CommandContext
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

    async def handle_commands(self, message: discord.Context) -> None:
        """
        Handles any commands given through the designed character
        """
        
        command = message.content.replace(self._bot.guild_config[message.guild_id]['command_character'], '')
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
            query['id'] = sticker_id

        if name is not None:
            query['name'] = name

        sticker = self._db.get_sticker(query)

        return sticker

    def update_sticker(self, *, message:discord.Context) -> None:
        """
        Updates info about sticker(s)
        """

        for sticker_info in message.sticker_items:
            sticker = self._db.get_sticker({'id': sticker_info['id']})

            if not sticker:
                sticker = self._db.create_sticker(sticker_info, message.guild_id, message.channel_id)

            else:
                sticker = self._db.update_sticker_stats(sticker=sticker, channel_id=message.channel_id)
