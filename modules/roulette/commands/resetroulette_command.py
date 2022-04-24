# -*- coding: utf-8 -*-

## RouletteCommand ##
# A command to randomly timeout someone. #

import asyncio
import random
import json

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log

class ResetRouletteCommand(Command):
	"""
	!resetroulette @user|ID
	!rr @user|ID
	"""

	def __init__(self, roulette, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(roulette, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'resetroulette'}, context=context)

		user_id = None

		# We either need a mention or an ID as first parameter.
		if not context.mentions:
			user_id = context.params[0]
			# review its a "valid" snowflake
			if not len(user_id) > 16:
				await self.send_help(context)
				return

		else:
			user_id = context.mentions[0]['id']

		# reset from cache
		self._module.remove_user_from_cache(user_id)

		# react to message
		await self._bot.http.create_reaction(context.channel_id, context.id, "✅")


	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}rr @user|ID to reset their cache on BH.", 'inline': False},
		]

		await self._bot.send_embed_message(context.channel_id, "Reset Roulette", fields=fields)
