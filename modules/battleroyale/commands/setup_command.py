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

class SetupBRCommand(Command):
	"""
	!setup_br
	"""

	def __init__(self, br, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(br, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:

		# check if there is a number as parameter
		if len(context.params) > 0 and context.params[0].isnumeric():
			self._module._max_participants = context.params[0]

		# First send rules message
		content = f'''
		**Mooncord Battle Royale**

		{self._module._max_participants} players will compete, {self._module._max_participants-1} will get pitted and only 1 will claim the #1 Victory Royale.

		Rules are as follow:
		- Click the 👑 to join. Once you join you can't leave.
		- The amount of time you get pitted for increases depending on how long you survive.
		-- Early rounds will get 1h and it will gradually increase up to 24h.
		- All the events and the people participating in them are **random**.

		If you win the #1 Victory Royale you get to live, and to brag about it until nobody cares anymore.
		'''

		await self._bot.send_embed_message(context.channel_id, "Battle Royale", content)

		# Then create the join message
		content = f"To join Battle Royale react with 👑\r\n\r\n\
		There are currently {len(self._module.participants)} / {self._module._max_participants} ready to battle."
		footer = {
			"text": f"{self._bot.guild_config[context.guild.id]['name']} · Made by Yui"
		}

		# Setup the button
		button_component = {
			"type": 2, # button
			"style": 2, # secondary or gray
			"label": "Join BR",
			"emoji": {
				"id": None,
				"name": "👑",
				"animated": False
			},
			"custom_id": "join_br_button"
		}

		action_row = {
			"type": 1,
			"components": [button_component]
		}

		setup_message = await self._bot.send_embed_message(context.channel_id, "Battle Royale", content, color=10038562, footer=footer, components=[action_row])
		self._module._setup_message = setup_message
		self._module.edit_entries.start()
