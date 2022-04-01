# -*- coding: utf-8 -*-

## Pitbot Module ##
# Takes care of timing out and releasing people #

import logging
import datetime
from typing import Optional, List, Union, Tuple

import discord
from discord.ext import tasks

from .database import PitBotDatabase
from modules.context import CommandContext, DMContext
from .commands import Timeout, BotConfig, Release, Strike, Roles, Help, Shutdown
from utils import iso_to_datetime, datetime_to_iso, date_string_to_timedelta

log: logging.Logger = logging.getLogger("pitbot")

class PitBot:

	def __init__(self, *, bot: discord.Client) -> None:
		"""
		:var bot discord.Client: The bot instance
		"""

		self._bot = bot
		self._db = PitBotDatabase(database=bot.db)

		self.commands = {
			"shutdown": Shutdown(self, 'admin'),
			"config": BotConfig(self, 'admin'),
			"timeout": Timeout(self, 'mod', ['ban', 'time', 'remaining', 'timeout']),
			"timeoutns": Timeout(self, 'mod', skip_strike=True),
			"release": Release(self, 'mod'),
			"strikes": Strike(self, 'mod', ['strikes', 'pithistory', 'history']),
			"roles": Roles(self, 'mod'),
			"help": Help(self, 'mod', ['help', 'elp'])
		}

		self.commands['ban'] = self.commands['timeout']

		self.dm_commands = {
			"timeout": self.commands['timeout'],
			"strikes": self.commands['strikes'],
			"help": self.commands['help']
		}

		self.ping_commands = {
			"timeout": self.commands['timeout'],
			"ban": self.commands['timeout']
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

	async def handle_dm_commands(self, message: discord.Context) -> None:
		"""
		Handles any commands given by a user through DMs
		"""
		
		for dm_command in self.dm_commands:
			for keyword in self.dm_commands[dm_command].dm_keywords:
				if keyword in message.content:
					await self.dm_commands[dm_command].dm(DMContext(self._bot, message))
					return
		return

	async def handle_ping_commands(self, message: discord.Context) -> None:
		"""
		Handles any commands given by a user through a ping
		"""

		command = message.content
		params = message.content.split()

		# We need to make sure that whoever pinged the bot used @sayo as first positional argument
		if len(params) <= 1:
			# we dont care about people just pinging the bot
			return
		
		if params[0] != f'<@!{self._bot.user.id}>':
			# we dont care about people pinging the bot as part of the message
			return

		command = params[1].lower()
		params = params[2:]

		if command in self.ping_commands:
			await self.ping_commands[command].ping(CommandContext(self._bot, command, params, message))
		return

	# Functionality

	# Timeouts related
	def get_user_timeout(self, user: dict, partial: Optional[bool] = True) -> Optional[dict]:
		"""
		Gets a timeout for a user. If no active timeouts are found returns None
		"""

		query = {'user_id': user['id'], 'status': 'active'}

		timeout = self._db.get_timeout(query, partial)

		return timeout

	def get_user_timeouts(self, user: dict, sort: Optional[Tuple[str, int]] = None, status: Optional[str] = None, partial: Optional[bool] = True) -> List[dict]:
		"""
		Gets a list of timeouts for a user.

		Status is used to filter.
		"""

		query = {'user_id': user['id']}

		if status:
			query['status'] = status

		timeouts = self._db.get_timeouts(query, sort, partial)

		return timeouts

	def add_timeout(self, *, user: dict, guild_id: int, time: int, issuer_id: int,
		reason: Optional[str] = 'No reason specified.', source: Optional[str] = 'command') -> Optional[dict]:
		"""
		Adds a timeout to a user
		"""
		
		timeout = self._db.create_timeout(user, guild_id, time, issuer_id, reason, source)

		return timeout

	def extend_timeout(self, *, user: dict, time: int) -> Optional[dict]:
		"""
		Extends the duration of an active timeout by specified amount
		"""

		params = {'time': time}
		query = {'user_id': user['id'], 'status': 'active'}

		timeout = self._db.update_timeout(params=params, query=query)

		return timeout

	def expire_timeout(self, *, user: dict) -> Optional[dict]:
		"""
		Sets a timeout as expired
		"""

		params = {'status': 'expired', 'updated_date': datetime.datetime.now().isoformat()}
		query = {'user_id': user['id'], 'status': 'active'}

		timeout = self._db.update_timeout(params=params, query=query)

		return timeout

	def delete_timeout(self, *, user: dict) -> Optional[dict]:
		"""
		Deletes a timeout from database
		"""

		query = {'user_id': user['id'], 'status': 'active'}

		timeout = self._db.delete_timeout(query=query)

		return timeout

	# Strikes related
	def get_user_strikes(self, user: dict, sort: Optional[Tuple[str, int]] = None, status: Optional[str] = None, partial: Optional[bool] = True) -> List[dict]:
		"""
		Gets all strikes of a user.

		If partial is false full information of strike will be sent.
		Including information about users.
		"""

		query = {'user_id': user['id']}

		if status:
			query['status'] = status

		strikes = self._db.get_strikes(query, sort, partial)

		return strikes

	def add_strike(self, *, user: dict, guild_id: int, issuer_id: int,
		reason: Optional[str] = 'No reason specified.') -> Optional[dict]:
		"""
		Adds a strike to a user.

		returns: created Strike
		"""

		strike = self._db.create_strike(user, guild_id, issuer_id, reason)

		return strike

	def expire_strike(self, *, user: dict, strike_id: int) -> Optional[dict]:
		"""
		Sets a strike as expired
		"""

		if strike_id == "oldest":
			# Get all active strikes, sort them by ID, get the ID of the latest
			strikes = self._db.get_strikes({'user_id': user['id'], 'status': 'active'})
			if len(strikes) <= 0:
				return None
			strike_id = str(strikes[0]['_id'])

		params = {'status': 'expired', 'updated_date': datetime.datetime.now().isoformat()}
		query = {'_id': strike_id, 'user_id': user['id'], 'status': 'active'}

		strike = self._db.update_strike(params=params, query=query)

		return strike

	def delete_strike(self, *, user: dict, strike_id: int = 'newest') -> Optional[dict]:
		"""
		Deletes a strike from database
		"""

		if strike_id == "newest":
			# Get all active strikes, sort them by ID, get the ID of the newest
			strikes = self._db.get_strikes({'user_id': user['id'], 'status': 'active'}, ('_id', -1))
			print(len(strikes))
			if len(strikes) <= 0:
				return None
			strike_id = str(strikes[0]['_id'])

		query = {'_id': strike_id, 'user_id': user['id'], 'status': 'active'}

		strike = self._db.delete_strike(query=query)

		return strike

	# Users related
	def get_user(self, *, user_id: Optional[str] = None, username: Optional[str] = None,
		discriminator: Optional[str] = None) -> Optional[dict]:
		"""
		Get a user from database.
		"""

		if user_id is not None:
			query = {'discord_id': user_id}
		elif username is not None and discriminator is not None:
			query = {'username': username, 'discriminator': discriminator}
		else:
			raise Exception("user_id or username and discriminator cannot be None.")

		user = self._db.get_user(query)
		if user:
			user['id'] = user['discord_id']

		return user