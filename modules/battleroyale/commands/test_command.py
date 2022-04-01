# -*- coding: utf-8 -*-

## SetupBRCommand Command ##
# A command to setup BR event. #

import asyncio
import discord
import random
import json

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log

class TestBRCommand(Command):
	"""
	!test_br
	"""

	def __init__(self, br, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(br, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:

		# check if there is a number as parameter
		for i in range(32):
			self._module.participants.append('539881999926689829')

		await self._module._bot.send_embed_message(self._module._setup_message['channel_id'], f"Added 32 participants")
