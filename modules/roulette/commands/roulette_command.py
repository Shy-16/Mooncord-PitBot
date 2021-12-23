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

	def __init__(self, roulette, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(roulette, permission, dm_keywords)

	async def execute(self, context: CommandContext) -> None:

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'roulette'}, context=context)

		if self._pitbot._cooldown > 0:
			info_message = f'Roulette command is on cooldown: {self._pitbot._cooldown} seconds left.'
			await self._bot.send_embed_message(context.channel_id, 'Roulette', info_message)
			return

		times = self._pitbot.user_in_cache(context.author['id'])

		if times:
			if times == 1:
				# Let the user know in the channel about the cooldown
				info_message = 'Roulette command may only be used once every 24h'
				await self._bot.send_embed_message(context.channel_id, 'Roulette', info_message)

			#if times >= 4:
			#	# The user is just spamming the bot so add a strike to their account along with a warning
			#	reason = 'User spamming the roulette command after being notified that can only be used every 12 hours.'
			#	strike_info = self._bot.pitbot_module.add_strike(user=context.author, guild_id=context.guild.id,
			#		issuer_id=self._bot.user.id, reason=reason)

			#	# Send a DM to the user
			#	info_message = f"A strike has been added to your {context.guild.name} account for spamming the roulette command\
			#		even after being notified that it can only be used once every 12 hours.\r\n\r\n\
			#		Please be warned that this strike has been issued because you've used the command at least 4 times which is\
			#		already considered enough to abuse a command."
			#	await self._bot.send_embed_dm(user['id'], "User Timeout", info_message)

			self._pitbot.add_user_to_cache(context.author['id'])
			return

		# Add the cooldown asap
		self._pitbot._cooldown = 60 # 1 minute

		# Lets begin the story
		stories = list()
		base_path = Path(__file__).parent
		file_path = (base_path / 'stories.json').resolve()

		with open(file_path, 'r+') as f:
			stories = json.load(f)

		story = stories[random.randint(0, len(stories)-1)]
		index = 0

		while(index < len(story)):
			step = story[index]

			if step['type'] == 'text':
				if step['typing']:
					await self._bot.http.trigger_typing(context.channel_id)

				if step['interval']:
					await asyncio.sleep(step['interval'])

				# Send message in channel
				await self._bot.send_message(context.channel_id, step['value'].format(name=context.author['username']))

				index += 1

				if step.get('end'):
					index = 10000

			elif step['type'] == 'wait':
				await asyncio.sleep(step['interval'])

				index += 1

			elif step['type'] == 'roll':
				# Roll to see if the user dies or not.
				roll = random.randint(0, step['chances']-1)

				if roll == 0:
					# User lost
					index = step['lose']

					# Time them out
					# Default reason is
					reason = 'Automatic timeout issued for losing the roulette'

					# Issue the timeout
					timeout_info = self._bot.pitbot_module.add_timeout(user=context.author, guild_id=context.guild.id,
						time=3600, issuer_id=self._bot.user.id, reason=reason)

					# Add the roles
					for role in context.ban_roles:
						await self._bot.http.add_member_role(context.guild.id, context.author['id'], role, reason)

					# generate logs in proper channel
					if context.log_channel:
						# Send information of the message caught
						info_message = f"<@{context.author['id']}> was timed out for 1h losing the roulette."
						await self._bot.send_embed_message(context.log_channel, "Roulette losers", info_message)

					# Send a DM to the user
					info_message = f"You've been pitted by {context.guild.name} mod staff for 2h for losing the roulette. \r\n\
						This timeout doesn't add any strikes to your acount.\r\n\r\n... loser."

					await self._bot.send_embed_dm(context.author['id'], "User Timeout", info_message)

				else:
					# User won
					index = step['win']

		self._pitbot.add_user_to_cache(context.author['id'])

	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}roulette to win or lose.", 'inline': False},
		]

		await self._bot.send_embed_message(context.channel_id, "Sticker Stats", fields=fields)
