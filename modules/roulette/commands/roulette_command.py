# -*- coding: utf-8 -*-

## RouletteCommand ##
# A command to randomly timeout someone. #

import asyncio
import random
import json
from pathlib import Path

from modules.pitbot.commands.context import CommandContext
from modules.pitbot.commands.command import Command
from log_utils import do_log

class RouletteCommand(Command):
	"""
	!roulette <bullets|optional> <triggers|optional>
	"""

	def __init__(self, roulette, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(roulette, permission, dm_keywords)

	async def execute(self, context: CommandContext) -> None:

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'roulette'}, context=context)

		# Check cache and add to cache
		times = self._pitbot.user_in_cache(context.author['id'])
		self._pitbot.add_user_to_cache(context.author['id'])

		if times:
			if times == 1:
				# Let the user know in the channel about the cooldown
				info_message = 'Roulette command may only be used once every 24h'
				await self._bot.send_embed_message(context.channel_id, 'Roulette', info_message)
			return

		# vars
		bullets = 1
		triggers = 1

		# Get params if any
		if len(context.params) >= 1:
			# bullets
			vb = context.params[0]
			if vb.isdigit():
				bullets = int(vb)
				if bullets > 5:
					bullets = 5
				elif bullets <= 0:
					bullets = 1

		if len(context.params) >= 2:
			# triggers
			vr = context.params[1]
			if vr.isdigit():
				triggers = int(vr)
				if triggers >= bullets:
					triggers = bullets -1
				elif triggers <= 0:
					triggers = 1


		if triggers <= 0: triggers = 1

		chamber = [0, 0, 0, 0, 0, 0]
		for i in range(bullets): chamber[i] = 1
		random.shuffle(chamber) 

		shots = list()

		for i in range(triggers):
			if chamber[i] == 0:
				shots.append("**Click...**")

			else:
				# Got shot.
				shots.append("**BANG!**")

				shots_string = "\r\n ".join(shots)

				# Send a smug notification on the channel
				description = f"<@{context.author['id']}> loads {bullets} bullets and pulls the trigger {triggers} time{'s' if triggers > 1 else ''}...\r\n \
					{shots_string}\r\n\r\nBACK TO THE PIT"

				image = {
					"url": self._bot.get_timeout_image(),
					"height": 0,
					"width": 0
				}

				await self._bot.send_embed_message(context.channel_id, "Roulette Loser", description, image=image)

				# Default reason
				reason = 'Automatic timeout issued for losing the roulette'

				# Issue the timeout
				timeout_info = self._bot.pitbot_module.add_timeout(user=context.author, guild_id=context.guild.id,
					time=3600*bullets, issuer_id=self._bot.user.id, reason=reason)

				# Add the roles
				for role in context.ban_roles:
					await self._bot.http.add_member_role(context.guild.id, context.author['id'], role, reason)

				# generate logs in proper channel
				if context.log_channel:
					# Send information of the message caught
					info_message = f"<@{context.author['id']}> was timed out for {bullets}h for losing the roulette."
					await self._bot.send_embed_message(context.log_channel, "Roulette losers", info_message)

				# Send a DM to the user
				info_message = f"You've been pitted by {context.guild.name} mod staff for {bullets}h for losing the roulette. \r\n\
					This timeout doesn't add any strikes to your acount.\r\n\r\n... loser."

				await self._bot.send_embed_dm(context.author['id'], "User Timeout", info_message)
				return

		shots_string = "\r\n ".join(shots)

		# Send a notification on the channel
		description = f"<@{context.author['id']}> loads {bullets} bullets and pulls the trigger {triggers} time{'s' if triggers > 1 else ''}...\r\n \
			{shots_string}"

		await self._bot.send_embed_message(context.channel_id, "Roulette Winner", description)

	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}roulette to win or lose.", 'inline': False},
		]

		await self._bot.send_embed_message(context.channel_id, "Sticker Stats", fields=fields)
