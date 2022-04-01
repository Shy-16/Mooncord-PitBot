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

class StartBRCommand(Command):
	"""
	!start_br
	"""

	def __init__(self, br, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(br, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:

		# disable button so players can't join after it starts
		button_component = {
			"type": 2, # button
			"style": 2, # secondary or gray
			"label": "Join BR",
			"emoji": {
				"id": None,
				"name": "👑",
				"animated": False
			},
			"custom_id": "join_br_button",
			"disabled": True
		}

		action_row = {
			"type": 1,
			"components": [button_component]
		}

		payload = {
			'components': [action_row]
		}

		await self._bot.http.edit_message(self._module._setup_message['channel_id'], self._module._setup_message['id'], payload)

		# First send rules message
		content = '''
		**Mooncord Battle Royale**

		Starting now!
		'''

		await self._bot.send_embed_message(context.channel_id, "Battle Royale", content)

		self._module._started = True
		self._module.generate_event.start()
