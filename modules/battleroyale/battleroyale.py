# -*- coding: utf-8 -*-

## Roulette Module ##
# Fluff roulette minigame where people gamble a pit #

import logging
import datetime
import random
from numpy.random import choice
import asyncio
from typing import Optional, List, Union, Tuple

import discord
from discord.ext import tasks

from modules.context import CommandContext
from .commands import SetupBRCommand, StartBRCommand, TestBRCommand
from .components import handle_join_br_button
from .event import Event, events, weights

log: logging.Logger = logging.getLogger("br")

class BattleRoyale:

	def __init__(self, *, bot: discord.Client) -> None:
		"""
		:var bot discord.Client: The bot instance
		"""

		self._bot = bot

		self._edit_cd = False
		self._setup_message = None

		# br related
		self.participants = list()
		self._max_participants = 128
		self._started = False
		self._round = 1

		self._friendships = []

		self.commands = {
			"setup_br": SetupBRCommand(self, 'mod'),
			"start_br": StartBRCommand(self, 'mod'),
			"test_br": TestBRCommand(self, 'mod')
		}

	@tasks.loop(minutes=1)
	async def edit_entries(self) -> None:
		if self._edit_cd:
			self._edit_cd = False

			# Change content and edit embed
			content = f"To join Battle Royale react with 👑\r\n\r\n\
			There are currently {len(self.participants)} / {self._max_participants} ready to battle."

			embed = self._setup_message['embeds'][0]
			embed['description'] = content

			payload = {
				'embeds': [embed]
			}

			await self._bot.http.edit_message(self._setup_message['channel_id'], self._setup_message['id'], payload)


	def init_tasks(self) -> None:
		"""
		Initialize the different tasks that run in the background
		"""
		
		handle_join_br_button(self._bot)

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

	async def timeout_user(self, user_id: str) -> None:
		"""
		Times the given user through discord feature and not a pit
		"""

		# don't hate me for hardcoding this
		guild_id = '193277318494420992'

		timeout = (datetime.datetime.utcnow() + datetime.timedelta(hours=min(self._round, 24))).isoformat()
		data = {'communication_disabled_until': timeout}

		response = await self._bot.http.modify_member(user_id, guild_id, data)

	def draw_event(self) -> Event:
		"""
		Draw an event from the pool and make sure it can be run
		"""

		event = None
		players = len(self.participants)
		_valid = False

		while not _valid:
			event = choice(events, size=1, replace=False, p=weights)[0]
			if event.players <= len(self.participants):
				_valid = True

		return event

	def run_event(self, all_losers: list, event: Event=None, players: list=None) -> dict:
		"""
		Run an event and return a field to send to discord
		"""

		# draw one event randomly from the pool
		if event:
			_event = event
		else:
			_event = self.draw_event()

		# execute event
		if players:
			_users, _template = _event.execute(self, players)
		else:
			_users, _template = _event.execute(self)

		# add losers and remove losers
		if _event.has_losers:
			all_losers.extend(_users)
			self.participants = [user for user in self.participants if user not in all_losers]

		# generate the field event
		return {'name': _event.name, 'value': _template, 'inline': False}

	# Functionality
	@tasks.loop(seconds=30)
	async def generate_event(self) -> None:
		fields = []
		all_losers = []

		if self._started:
			# Check how many people are left
			# 5 or more pull an event as always
			if len(self.participants) > 4:
				field = self.run_event(all_losers)
				fields.append(field)

				# if number of players left is greater than a set amount do more events, up to 3
				if len(self.participants) > 8:
					# draw another event
					field = self.run_event(all_losers)
					fields.append(field)

				# if number of players is greater than a set do one more
				if len(self.participants) > 16:
					# draw another event
					field = self.run_event(all_losers)
					fields.append(field)

				# print messages in chat
				fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
				await self._bot.send_embed_message(self._setup_message['channel_id'], f"Round {self._round}", fields=fields)

				# sleep for 10 seconds then pit all losers
				await asyncio.sleep(10)

				for loser in all_losers:
					# Issue the timeout
					await self.timeout_user(loser)

					# check and remove friendships with this user
					self._friendships = [friends for friends in self._friendships if friends[0] != loser and friends[1] != loser]

					# sleep for 2 seconds so we don't get rate limited
					await asyncio.sleep(2)

				# increase round by 1
				self._round += 1

			# 4 or less = do 2 events of duel.
			elif len(self.participants) in [3, 4]:
				if len(self.participants) == 4:
					split_1 = [self.participants[0], self.participants[1]]
					split_2 = [self.participants[2], self.participants[3]]
					field = self.run_event(all_losers, events[0], split_1)
					fields.append(field)
					field = self.run_event(all_losers, events[0], split_2)
					fields.append(field)
				else:
					field = self.run_event(all_losers, events[0], [self.participants[0], self.participants[1]])
					fields.append(field)

				# increase round by 1
				self._round += 1

			# 2 or less = do a duel and announce winner
			elif len(self.participants) <= 2:
				field = self.run_event(all_losers, events[0], [self.participants[0], self.participants[1]])
				fields.append(field)
				await self._bot.send_embed_message(self._setup_message['channel_id'], f"Round {self._round}", fields=fields)

				# announce winner
				description= f'''
				Mooncord 2022 Battle Royale Winner.

				<@{self.participants[0]}>

				'''
				await self._bot.send_embed_message(self._setup_message['channel_id'], f"Battle Royale Winner", description)
				self.generate_event.stop()
