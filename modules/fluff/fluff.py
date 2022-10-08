# -*- coding: utf-8 -*-

## Stickers Module ##
# Shows different stats for sticker usage #

import logging
import datetime
from typing import Optional, List, Union, Tuple

import discord

from modules.context import CommandContext
from .commands import ExecuteCommand

log: logging.Logger = logging.getLogger("fluff")

class Fluff:

	def __init__(self, *, bot: discord.Client) -> None:
		"""
		:var bot discord.Client: The bot instance
		"""

		self._bot = bot

		self.commands = {
		}

		self.ping_commands = {
			"execute": ExecuteCommand(self, 'mod'),
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
		
		command = message.content.replace(self._bot.guild_config[message.guild_id]['command_character'], '')
		params = list()

		if ' ' in command:
			command, params = (command.split()[0], command.split()[1:])

		command = command.lower()
		
		if command in self.commands:
			await self.commands[command].execute(CommandContext(self._bot, command, params, message))
		return

	async def handle_ping_commands(self, message: str) -> None:
		"""
		Handles any commands given by a user through a ping
		"""

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
