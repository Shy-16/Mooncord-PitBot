# -*- coding: utf-8 -*-

## Pitbot Module ##
# Takes care of timing out and releasing people #

import logging
import datetime
from typing import Optional, List, Union

import discord
from discord.ext import tasks

from .database import PitBotDatabase
from .commands import CommandContext, DMContext, Timeout, BotConfig, Release, Strike, Roles, Help, Close, Shutdown
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
		self.free_users.start()

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
					await self.dm_commands[dm_command].dm(DMContext(self, message))
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
		
		if params[0] != f'<@!{self.user.id}>':
			# we dont care about people pinging the bot as part of the message
			return

		command = params[1].lower()
		params = params[2:]

		if command in self.ping_commands:
			await self.ping_commands[command].ping(CommandContext(self, command, params, message))
		return

	# Task scheduler
	@tasks.loop(seconds=60)
	async def free_users(self) -> None:
		if not self._bot.is_ready():
			return

		timeouts = self._bot.db.get_all_timeouts()
		timeouts = list(timeouts)

		for timeout in timeouts:
			issued_date = iso_to_datetime(timeout['created_date'])
			expire_date = issued_date + datetime.timedelta(seconds=timeout['time'])

			user = await self._bot.http.get_user(timeout['user_id'])
			guild = await self._bot.http.get_guild(timeout['guild_id'])
			member = None
			if user is not None:
				member = await self._bot.http.get_member(guild['id'], user['id'])

			if datetime.datetime.now() >= expire_date:
				if user is not None:
					timeout_info = self._db.remove_user_timeout(user)
				else:
					timeout_info = self._db.remove_user_timeout(timeout['user_id'])

				if not member:
					return

				for role in self.guild_config[guild['id']]['ban_roles']:
					await self.http.remove_member_role(guild['id'], user['id'], role, reason="Timeout expired.")

				if not self.is_silent(timeout_info['guild_id']):
					await self.send_embed_message(self.guild_config[guild.id]['log_channel'], "User Released",
						fields=[{'name': 'Info', 'value': f"User: <@{user.id}> was just released from the pit.", 'inline': False}])

				# Send a DM to the user
				fields = [{'name': 'Timeout', 'value': f"Your timeout in {guild.name} has expired and you've been released from the pit.", 'inline': False},
					{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
						to get a summary of your disciplinary history on {guild.name}.", 'inline': False}
				]

				await self.send_embed_dm(member, "User Timeout", fields=fields)

				await do_log(place="auto_task",
				   data_dict={'event': 'auto_release', 'author_id': self.user.id, 'author_handle': f'{self.user.name}#{self.user.discriminator}'},
				   member=member)

	# Functionality

	# Timeouts related
	def get_user_timeout(self, user: dict) -> Optional[dict]:
		"""
		Gets a timeout for a user. If no active timeouts are found returns None
		"""

		query = {'user_id': user['id'], 'status': 'active'}

		timeout = self._db.get_timeout(query)

		return timeout

	def get_user_timeouts(self, user: dict, status: str = 'active') -> List[dict]:
		"""
		Gets a list of timeouts for a user.

		Status is used to filter.
		"""

		query = {'user_id': user['id'], 'status': status}

		timeout = self._db.get_timeout({'user_id': user['id'], 'status': 'active'})

		return timeout

	def add_timeout(self, *, user: dict, guild_id: int, time: int, issuer_id: int,
		reason: Optional[str] = 'No reason specified.') -> Optional[dict]:
		
		timeout = self._db.create_timeout(user, guild_id, time, issuer_id, reason)

		return timeout

	def extend_timeout(self, *, user: dict, time: int) -> Optional[dict]:
		"""
		Extends the duration of an active timeout by specified amount
		"""

		params = {'time': time}
		query = {'user_id': user['id'], 'status': 'active'}

		timeout = self._db.update_timeout(params=params, query=query)

		return timeout

	# Strikes related
	def get_user_strikes(self, user: dict) -> List[dict]:
		"""
		Gets all strikes of a user
		"""

		query = {'user_id': user['id'], 'status': 'active'}

		strikes = self._db.get_strikes(query)

		return strikes

	def add_strike(self, *, user: dict, guild_id: int, issuer_id: int,
		reason: Optional[str] = 'No reason specified.') -> Optional[dict]:
		"""
		Adds a strike to a user.

		returns: created Strike
		"""

		strike = self._db.create_strike(user, guild_id, issuer_id, reason)

		return strike

