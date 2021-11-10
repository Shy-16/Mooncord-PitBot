# -*- coding: utf-8 -*-

## Modmail Module ##
# Interacts with Modmail functionality through API #

import asyncio
import math
from thefuzz import fuzz, process

import discord
from discord.ext import tasks

from utils import iso_to_datetime, seconds_to_string
from log_utils import do_log

class Banwords:

	def __init__(self, bot):
		"""
		@bot: Sayo
		"""
		self._bot = bot
		self._db = bot.db

		self.banwords = list()
		self.banword_list = list()

	def init_tasks(self):
		self.refresh_banword_cache.start()

	@tasks.loop(seconds=300)
	async def refresh_banword_cache(self):
		banwords = self._db.get_banwords()
		self.banwords = list(banwords)
		self.banword_list = [banword['word'] for banword in banwords]

	async def handle_message(self, message: discord.Context) -> None:
		"""
		Handles a new message caught to the bot that didnt fall into any command category
		and was written in a public channel, not in DMs
		"""

		# Get banwords from bot
		matches = process.extract(context.message.content, self._bot.banword_list, scorer=fuzz.partial_ratio)

		for match in matches:
			for banword in self._bot.banwords:
				if banword['word'] == match[0]:
					if match[1] >= banword['strength']:
						# Timeout user based on selected configuration
						await self.do_timeout(banword, context)
						return

	async def do_timeout(self, banword, context):
		# Check if its inside a link and if we allow links or not.
		if context.message.content.startswith("http") and not banword['include_link']:
			return

		# Get user information and user strikes
		user_strikes = self._bot.db.get_user_strikes(context.author)

		# First check base duration
		duration = banword['duration'] # in seconds

		# Then check if variable time is selected.
		increment = 0

		if banword['variable_time']:
			# Add incremental time per strike on the user.
			increment = duration * math.pow(user_strikes.count(), 2)

		# Handle temporary and permanent bans
		# TODO:

		# Default reason is
		reason = 'Automatic timeout issued for typing a banned word: ({})'.format(banword['word'])

		# Issue the timeout
		timeout_info = self._bot.db.add_user_timeout(context.author, context.guild, duration+increment, self._bot.user, reason)

		# Add the roles
		for role in context.ban_roles:
			await context.author.add_roles(context.guild.get_role(role), reason='Automatic timeout issued for typing a banned word: ({})'.format(banword['word']))
		
		await do_log(place="guild", data_dict={'event': 'timeout', 'command': 'banword'}, message=context.message)

		# generate logs in proper channel
		if context.log_channel:
			user_timeouts = self._bot.db.get_user_timeouts(context.author, {'status': 'expired'})

			strike_text = ""
			if user_strikes.count() > 0:
				strike_messages = list()

				for strike in user_strikes.sort('_id', -1)[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = context.guild.get_member(strike['issuer_id'])
					strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{context.author.id}> was timed out for {seconds_to_string(duration+increment)} for typing a banned word: {banword['word']} \r\n\
			The timeout has a {seconds_to_string(duration)} base duration with {seconds_to_string(increment)} additional time from previous strikes."

			fields = [
				{'name': 'Issue', 'value': info_message, 'inline': False},
				{'name': 'Timeouts', 'value': f"<@{context.author.id}> has {user_timeouts.count()} previous timeouts.", 'inline': False},
				{'name': 'Strikes', 'value': f"<@{context.author.id}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "User Timeout", fields=fields)

		# Send a DM to the user
		info_message = f"You've been pitted by {context.guild.name} mod staff for {seconds_to_string(duration+increment)} for \
			typing a banned word: {banword['word']} \r\n\
			The timeout has a {seconds_to_string(duration)} base duration with {seconds_to_string(increment)} additional time from previous strikes."

		fields = [
			{'name': 'Timeout', 'value': info_message, 'inline': False},
			{'name': 'Strikes', 'value': f"You currently have {user_strikes.count()} active strikes in {context.guild.name} (including this one).\r\n"+
				f"If you receive a few more pits, your following punishments will be escalated--most likely to a temporary or permanent ban.", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on Mooncord.", 'inline': False}
		]

		await self._bot.send_embed_dm(context.author, "User Timeout", fields=fields)

