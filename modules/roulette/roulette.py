# -*- coding: utf-8 -*-

## Roulette Module ##
# Fluff roulette minigame where people gamble a pit #

import logging
from typing import Union, Any

import datetime
import discord
from discord.ext import tasks

from modules.context import CommandContext, InteractionContext
from .commands import RouletteCommand, BulletHellCommand, ResetRouletteCommand

log: logging.Logger = logging.getLogger("roulette")


class Roulette:
    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot = bot
        self._cache = {}
        self._timeouts = []
        self._reset_time = datetime.time(20, tzinfo=datetime.timezone.utc)

        self.commands = {
            "roulette": RouletteCommand(self, 'any'),
            "bullethell": BulletHellCommand(self, 'any'),
            "resetroulette": ResetRouletteCommand(self, 'mod')
        }

        self.commands['rouiette'] = self.commands['roulette']
        self.commands['bh'] = self.commands['bullethell']
        self.commands['rr'] = self.commands['resetroulette']

    @tasks.loop(hours=1)
    async def refresh_cache(self) -> None:
        if datetime.datetime.now(datetime.timezone.utc).hour == self._reset_time.hour:
            self._cache = {}

    @tasks.loop(minutes=20)
    async def report_timeouts(self) -> None:
        losers = ", ".join(self._timeouts)
        if losers and len(losers) > 1:
            await self._bot.send_embed_message(self._bot.default_guild['log_channel'], "Roulette losers", losers)
        self._timeouts.clear()

    def init_tasks(self) -> None:
        """Initialize the different asks that run in the background"""
        self.refresh_cache.start()
        # self.report_timeouts.start()

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
    def user_in_cache(self, user_id: str) -> Union[dict, bool]:
        """Verifies if given user_id is already in cache"""
        if user_id in self._cache:
            return self._cache[user_id]
        return False

    def add_user_to_cache(self, user_id: str) -> None:
        """Adds user to cache"""
        if not user_id in self._cache:
            self._cache[user_id] = 1
        else:
            self._cache[user_id] += 1

    def remove_user_from_cache(self, user_id: str) -> None:
        """Removes user from cache"""
        if user_id in self._cache:
            self._cache.pop(user_id)

    def get_reset_time(self):
        """Returns a timestamp reset time"""
        # calculate reset time of next day
        now = datetime.datetime.now(datetime.timezone.utc)
        reset = datetime.datetime.now(datetime.timezone.utc).replace(hour=self._reset_time.hour, minute=0, second=0, microsecond=0)
        if now.hour > self._reset_time.hour:
            reset = reset + datetime.timedelta(days=1)
        return int(reset.timestamp())

    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "Roulette module adds commands that user can use to pit themselves based on random chances."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'roulette', 'value': f"{context.command_character}roulette will simulate a russian roulette.\r\n"+ 
                "It takes 2 parameters: number of bullets and number of shots. The chamber will be spinned once then shoot in succession.\r\n\r\n"+
                f"Example command: {context.command_character}roulette 3 3", 'inline': False},
            {'name': 'bullet hell | bh', 'value': f"{context.command_character}bh will shoot multiple bullets with increasing chances to be pitted.\r\n"+ 
                """```
lead: 1/2 2h
silver: 1/4 4h
gold: 1/8 8h
platinum: 1/24 12h
diamond: 1/32 16h
obsidian: 1/48 24h
cosmic: 1/72 36h
shiny: 1/4096 48h
```\r\n\r\n"""+
                f"Example command: {context.command_character}bh", 'inline': False},
        ]
        return {
            "title": "Roulette Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
