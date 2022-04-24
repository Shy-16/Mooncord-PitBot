# -*- coding: utf-8 -*-

## RouletteCommand ##
# A command to randomly timeout someone. #

import asyncio
import random
import json

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log

class ExecuteCommand(Command):
	"""
	@Pit Bot execute order 66
	"""

	def __init__(self, roulette, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(roulette, permission, dm_keywords)

	@verify_permission
	async def ping(self, context):
		# react to message
		await self._bot.http.create_reaction(context.channel_id, context.id, "✅")

		# send a message back
		await self._bot.send_message(context.channel_id, "Executing order 66. No one shall be spared, not even the children.")

	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}rr @user|ID to reset their cache on BH.", 'inline': False},
		]

		await self._bot.send_embed_message(context.channel_id, "Reset Roulette", fields=fields)
