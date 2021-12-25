# -*- coding: utf-8 -*-

## BulletHell Command ##
# A command to randomly timeout someone. #

import asyncio
import random
import json

from modules.pitbot.commands.context import CommandContext
from modules.pitbot.commands.command import Command
from log_utils import do_log

class BulletHellCommand(Command):
	"""
	!bullethell <type|optional|all>
	!bh
	!bh all
	!bh silver
	"""

	def __init__(self, roulette, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(roulette, permission, dm_keywords)

	async def execute(self, context: CommandContext) -> None:

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'bullethell'}, context=context)

		# Check cache and add to cache
		times = self._pitbot.user_in_cache(context.author['id'])
		#self._pitbot.add_user_to_cache(context.author['id'])

		if times:
			# Let the user know in the channel about the cooldown
			info_message = f'You may use Roulette command only once a day. \r\n\
				Next reset cooldown is {self._pitbot.get_reset_time()}'
			await self._bot.send_embed_dm(context.author['id'], 'Roulette Info', info_message)
			return

		# vars
		lead = {'name': 'Lead', 'odds': 6, 'timeout': 3600} # 1h
		silver = {'name': 'Silver', 'odds': 16, 'timeout': 7200} # 2h
		gold = {'name': 'Gold', 'odds': 32, 'timeout': 14400} # 4h
		diamond = {'name': 'Diamond', 'odds': 64, 'timeout': 28800} # 8h
		platinum = {'name': 'Platinum', 'odds': 128, 'timeout': 57600} # 16h
		cosmic = {'name': 'Cosmic', 'odds': 512, 'timeout': 86400} # 24h
		shiny = {'name': 'Shiny', 'odds': 4096, 'timeout': 172800} # 48h

		bullets = [shiny, cosmic, platinum, diamond, gold, silver, lead]
		mods = [
			'468937023307120660', # Moon
			'186562579412418560', # Amaya
			'178015162287128576', # Brock
			'157411268624384002', # Cheeky
			'177904844412026880', # Duke
			 '69945889182986240', # Grimace
			'117373803344035841', # Jestar
			'187308638321246209', # Kyro
			 '66292645407760384', # IpN
			'115843971804037120', # Nyx
			'184528528572678145', # Shy
			'109782272663629824', # Sunshine
			'539881999926689829', # Yui
		]

		for bullet in bullets:
			acc = random.randint(1, bullet['odds'])

			if acc == bullet['odds']:
				# Player got shot
				mod = mods[random.randint(0, len(mods)-1)]
				timeout = int(bullet['timeout']/3600)

				# Send a smug notification on the channel
				description = f"<@{context.author['id']}> stands tall in front of the mod team, ready to face their destiny.\r\n \
					The mod team prepares their set of 7 bullets and take aim, breathe in and...\r\n \
					**BANG!** A {bullet['name']} bullet shot by <@{mod}> went straight through <@{context.author['id']}>'s skull\
					obliterating their body and throwing their existence into dust.\r\n\r\n\
					BACK TO THE PIT for {timeout} hour{'s' if timeout > 1 else ''}"

				await self._bot.send_embed_message(context.channel_id, "Bullet Hell Loser", description)

				# Default reason
				reason = 'Automatic timeout issued for losing the bullet hell'

				# Issue the timeout
				timeout_info = self._bot.pitbot_module.add_timeout(user=context.author, guild_id=context.guild.id,
					time=timeout, issuer_id=self._bot.user.id, reason=reason)

				# Add the roles
				for role in context.ban_roles:
					await self._bot.http.add_member_role(context.guild.id, context.author['id'], role, reason)

				# generate logs in proper channel
				if context.log_channel:
					# Send information of the message caught
					info_message = f"<@{context.author['id']}> was timed out for {timeout}h for losing the bullet hell."
					await self._bot.send_embed_message(context.log_channel, "Bullet Hell Loser", info_message)

				# Send a DM to the user
				info_message = f"You've been pitted by {context.guild.name} mod staff for {timeout}h for losing the Bullet Hell. \r\n\
					This timeout doesn't add any strikes to your acount.\r\n\r\n... loser."

				await self._bot.send_embed_dm(context.author['id'], "Bullet Hell Loser", info_message)
				return

		# Send a notification on the channel
		description = f" "
		description = f"<@{context.author['id']}> stands tall in front of the mod team, ready to face their destiny.\r\n \
					The mod team prepares their set of 7 bullets and take aim, breathe in and...\r\n \
					*thud* *thunk* All the bullets miss the mark hitting the wall behind <@{context.author['id']}>\r\n\r\n \
					Looks like they will live another day."

		await self._bot.send_embed_message(context.channel_id, "Roulette Winner", description)

	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}bullethell or {context.command_character}bh to win or lose.", 'inline': False},
		]

		await self._bot.send_embed_message(context.channel_id, "Bullet Hell Info", fields=fields)
