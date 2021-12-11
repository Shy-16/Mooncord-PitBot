# -*- coding: utf-8 -*-

## Modmail Module ##
# Interacts with Modmail functionality through API #

import math
from thefuzz import fuzz, process

import discord
from discord.ext import tasks

from ..pitbot.commands import CommandContext
from utils import iso_to_datetime, seconds_to_string
from log_utils import do_log

class Banwords:

	def __init__(self, bot: discord.Client) -> None:
		self._bot = bot
		self._db = bot.db
		self._pitbot = bot.pitbot_module

		self.banwords = list()
		self.banword_list = list()

	def init_tasks(self):
		self.refresh_banword_cache.start()

	@tasks.loop(seconds=300)
	async def refresh_banword_cache(self) -> None:
		banwords = self._db.get_banwords({'active': True})
		self.banwords = list(banwords)
		self.banword_list = [banword['word'] for banword in banwords]

	async def handle_message(self, ctx: discord.Context) -> None:
		"""
		Handles a new message caught to the bot that didnt fall into any command category
		and was written in a public channel, not in DMs
		"""

		context = CommandContext(self._bot, "", "", ctx)

		# replace l33t and assign it to a new variable
		message = context.content.replace('0', 'o').replace('1', 'i').replace('3', 'e').replace('4', 'a').replace('5', 's')
		rmessage = message[::-1]

		split = message.split()

		for word in split:
			for banword in self.banwords:
				# first look for exact match
				if word == banword['word'] or word[::-1] == banword['word']:
					await self.do_timeout(banword, context, ('exact', 100))
					return

				# next check for strength based on strict ratio
				ratio = fuzz.ratio(word, banword['word'])
				if ratio >= banword['strength']:
					await self.do_timeout(banword, context, ('ratio', ratio))
					return

				ratio = fuzz.ratio(word[::-1], banword['word'])
				if ratio >= banword['strength']:
					await self.do_timeout(banword, context, ('ratio', ratio))
					return

	async def do_timeout(self, banword: str, context: CommandContext, match = None) -> None:
		# Check if its inside a link and if we allow links or not.
		if context.content.startswith("http") and not banword['include_link']:
			return

		# ease of user
		user = context.author

		# Get user information and user strikes
		user_strikes = self._pitbot.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

		# First check base duration
		duration = banword['duration'] # in seconds

		# Then check if variable time is selected.
		increment = 0

		if banword['variable_time']:
			# Add incremental time per strike on the user.
			increment = duration * math.pow(len(user_strikes), 2)

		# Handle temporary and permanent bans
		# TODO:

		# Default reason is
		reason = 'Automatic timeout issued for typing a banned word: ({})'.format(banword['word'])

		# Issue the timeout
		timeout_info = self._pitbot.add_timeout(user=user, guild_id=context.guild.id,
			time=int(duration+increment), issuer_id=self._bot.user.id, reason=reason)

		# Issue the strike
		strike_info = self._pitbot.add_strike(user=user, guild_id=context.guild.id,
			issuer_id=self._bot.user.id, reason=reason)

		# Add the roles
		for role in context.ban_roles:
			reason='Automatic timeout issued for typing a banned word: ({})'.format(banword['word'])
			await self._bot.http.add_member_role(context.guild.id, user['id'], role, reason)
		
		await do_log(place="guild", data_dict={'event': 'timeout', 'command': 'banword'}, context=context)

		# generate logs in proper channel
		if context.log_channel:
			# Send information of the message caught
			info_message = f"<@{user['id']}> was found typing a banned word: {banword['word']} in the following sentence."

			fields = [
				{'name': 'Match', 'value': f"```{match}```"},
				{'name': 'Message', 'value': f"```{context.content}```"}
			]

			await self._bot.send_embed_message(context.log_channel, "Banword Info", info_message, fields=fields)

			# First send timeout info
			user_timeouts = self._pitbot.get_user_timeouts(user=user, status='expired')

			strike_text = "```No Previous Strikes```"
			if len(user_strikes) > 0:
				strike_messages = list()

				for strike in user_strikes[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
					strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{user['id']}> was timed out for {seconds_to_string(duration+increment)} for typing a banned word: {banword['word']} \r\n\
			The timeout has a {seconds_to_string(duration)} base duration with {seconds_to_string(increment)} additional time from previous strikes."

			fields = [
				{'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
				{'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
				{'name': '\u200B', 'value': strike_text, 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "User Timeout", info_message, fields=fields)

		# Send a DM to the user
		info_message = f"You've been pitted by {context.guild.name} mod staff for {seconds_to_string(duration+increment)} for \
			typing a banned word: {banword['word']} \r\n\
			The timeout has a {seconds_to_string(duration)} base duration with {seconds_to_string(increment)} additional time from previous strikes."

		fields = [
			{'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).\r\n"+
				f"If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
		]

		await self._bot.send_embed_dm(user['id'], "User Timeout", info_message, fields=fields)

		# Delete message
		# TODO:
