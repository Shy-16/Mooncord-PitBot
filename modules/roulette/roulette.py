# -*- coding: utf-8 -*-

## Roulette Module ##
# Fluff roulette minigame where people gamble a pit #

import logging
import datetime
from typing import Optional, List, Union, Tuple

import discord
from discord.ext import tasks

from modules.pitbot.commands.context import CommandContext
from .commands import RouletteCommand

log: logging.Logger = logging.getLogger("roulette")

class Roulette:

	def __init__(self, *, bot: discord.Client) -> None:
		"""
		:var bot discord.Client: The bot instance
		"""

		self._bot = bot
		self._cache = dict()
		self._executing = False

		self.commands = {
			"roulette": RouletteCommand(self, 'any'),
		}

	@tasks.loop(hours=12)
	async def refresh_cache(self) -> None:
		self._cache = dict()

	def init_tasks(self) -> None:
		"""
		Initialize the different asks that run in the background
		"""
		self.refresh_cache.start()

	async def handle_commands(self, message: discord.Context) -> None:
		"""
		Handles any commands given through the designed character
		"""

		if self._executing:
			return
		
		command = message.content.replace(self._bot.guild_config[message.guild_id]['command_character'], '')
		params = list()

		if ' ' in command:
			command, params = (command.split()[0], command.split()[1:])

		command = command.lower()
		
		if command in self.commands:
			await self.commands[command].execute(CommandContext(self._bot, command, params, message))
		return

	# Functionality
	def user_in_cache(self, user_id: str) -> Union[dict, bool]:
		"""
		Verifies if given user_id is already in cache
		"""

		if user_id in self._cache:
			return self._cache[user_id]

		return False

	def add_user_to_cache(self, user_id: str) -> None:
		"""
		Adds user to cache
		"""

		if not user_id in self._cache:
			self._cache[user_id] = 1

		else:
			self._cache[user_id] += 1
