# -*- coding: utf-8 -*-

## Timeout ##
# A command to timeout people. #

import datetime
import discord

from .context import CommandContext, DMContext
from .command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
from log_utils import do_log

class Timeout(Command):

	def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = list(), skip_strike: bool =False) -> None:
		super().__init__(pitbot, permission, dm_keywords)

		self.skip_strike = skip_strike

	@verify_permission
	async def execute(self, context: CommandContext) -> None:
		if len(context.params) == 0:
			await self.send_help(context)
			return

		if len(context.params) <= 1:
			await self.send_help(context)
			return

		if not context.mentions:
			await self.send_help(context)
			return

		mention = context.mentions[0]
		amount = context.params[1]
		delta = date_string_to_timedelta(amount)
		if not delta:
			await self.send_help(context)
			return

		reason = ''
		if len(context.params) >= 2:
			reason = ' '.join(context.params[2:])

		if not self.skip_strike:
			strike_info = self._pitbot.add_strike(user=mention, guild_id=context.guild.id,
				issuer_id=context.author['id'], reason=reason)

		timeout_info = self._pitbot.get_user_timeout(mention)
		extended = False

		if not timeout_info:
			timeout_info = self._pitbot.add_timeout(user=mention, guild_id=context.guild.id,
				time=int(delta.total_seconds()), issuer_id=context.author['id'], reason=reason)
		else:
			new_time = int(delta.total_seconds() + timeout_info['time'])
			timeout_info = self._pitbot.extend_timeout(user=mention, time=new_time)
			extended = True

		for role in context.ban_roles:
			await self._bot.http.add_member_role(context.guild.id, mention['id'], role, "Timeout issued by a mod.")
		
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'timeout'}, message=context.message)

		user_strikes = self._pitbot.get_user_strikes(mention)

		if not context.is_silent and context.log_channel:
			user_timeouts = self._pitbot.get_user_timeouts(user=mention, status='expired')

			strike_text = ""
			if user_strikes.count() > 0:
				strike_messages = list()

				for strike in user_strikes.sort('_id', -1)[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = await self._bot.http.get_member(context.guild.id, strike['issuer_id'])
					strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{mention['id']}> was timedout by <@{context.author['id']}> for {amount}."
			if extended:
				info_message = f"<@{mention['id']}>'s timeout has been extended by <@{context.author['id']}> for {amount}."

			fields = [
				{'name': 'Issue', 'value': info_message, 'inline': False},
				{'name': 'Timeouts', 'value': f"<@{mention['id']}> has {user_timeouts.count()} previous timeouts.", 'inline': False},
				{'name': 'Strikes', 'value': f"<@{mention['id']}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "User Timeout", fields=fields)

		# Send a DM to the user
		info_message = f"You've been pitted by {context.guild.name} mod staff for {amount} for the following reason:\n\n{reason}"
		if extended:
			info_message = f"Your active timeout in {context.guild.name} has been extended by {amount} for the following reason:\n\n{reason}"

		fields = [
			{'name': 'Ban', 'value': info_message, 'inline': False},
			{'name': 'Strikes', 'value': f"You currently have {user_strikes.count()} active strikes in {context.guild.name} (including this one).\r\n"+
				f"If you receive a few more pits, your following punishments will be escalated--most likely to a temporary or permanent ban.", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on Mooncord.", 'inline': False}
		]

		await self._bot.send_embed_dm(mention, "User Timeout", fields=fields)

	async def dm(self, context):

		timeout = self._bot.db.get_user_timeout(context.author)

		if not timeout or timeout is None:
			fields = [
				{'name': 'Timeout Info', 'value': f"You dont have an active timeout right now.", 'inline': False}
			]

			await self._bot.send_embed_dm(context.author, "User Timeout", fields=fields)
			return

		guild = self._bot.get_guild(timeout['guild_id'])

		issued_date = iso_to_datetime(timeout['created_date'])
		expire_date = issued_date + datetime.timedelta(seconds=timeout['time'])
		delta = expire_date - datetime.datetime.now()
		expires_in = seconds_to_string(int(delta.total_seconds()))

		reason = ''
		if timeout['reason']: reason = f" with reason: {timeout['reason']}"

		fields = [
			{'name': 'Info', 'value': f"You have an active timeout in {guild.name}.\r\nIt will expire in {expires_in}", 'inline': False},
			{'name': 'Mods', 'value': f"Timeout was for: {reason}. Type `strikes` to get more information about your strikes.", 'inline': False}
		]

		await self._bot.send_embed_dm(context.author, "User Timeout", fields=fields)
		await do_log(place="dm", data_dict={'event': 'command', 'command': 'timeout', 'author_id': context.author.id,
				   			  'author_handle': f'{context.author.name}#{context.author.discriminator}'})

	@verify_permission
	async def ping(self, context):
		if len(context.mentions) < 2:
			return

		# the way this command works is as follows:
		# ["<@!mention_id>", "for", "30d", "for", "reason1", "reason2"..., "reasonN"]

		mention = context.mentions[1] # by now we've already stablished mentions 0 is the bot
		amount = context.params[2]
		delta = date_string_to_timedelta(amount)
		if not delta:
			return

		reason = ''
		if len(context.params) > 4:
			reason = ' '.join(context.params[4:])

		for role in context.ban_roles:
			await mention.add_roles(context.guild.get_role(role), reason="Timeout issued by a mod.")
		timeout_info = self._bot.db.add_user_timeout(mention, context.guild, int(delta.total_seconds()), context.author, reason)
		strike_info = self._bot.db.add_strike(mention, context.guild, context.author, reason)
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'timeout'}, message=context.message)

		user_strikes = self._bot.db.get_user_strikes(mention)

		if not context.is_silent and context.log_channel:
			# Send a smug notification on the channel
			fields = [
				{'name': 'Info', 'value': f"<@{mention.id}> has been sent to the pit for {amount} <:moon2H:814618028691161152>", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel, "User Timeout", fields=fields)

			user_timeouts = self._bot.db.get_user_timeouts(mention, {'status': 'expired'})

			strike_text = ""
			if user_strikes.count() > 0:
				strike_messages = list()

				for strike in user_strikes.sort('_id', -1)[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = context.guild.get_member(strike['issuer_id'])
					strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason']} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			fields = [
				{'name': 'Issue', 'value': f"<@{mention.id}> was timedout by <@{context.author.id}> for {amount}.", 'inline': False},
				{'name': 'Timeouts', 'value': f"<@{mention.id}> has {user_timeouts.count()} previous timeouts.", 'inline': False},
				{'name': 'Strikes', 'value': f"<@{mention.id}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "User Timeout", fields=fields)

		# Send a DM to the user
		fields = [
			{'name': 'Ban', 'value': f"You've been pitted by {context.guild.name} mod staff for {amount} \
				for the following reason:\n\n{reason}", 'inline': False},
			{'name': 'Strikes', 'value': f"You currently have {user_strikes.count()} active strikes in {context.guild.name} (including this one).\r\n"+
				f"If you receive a few more pits, your following punishments will be escalated--most likely to a temporary or permanent ban.", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on Mooncord.", 'inline': False}
		]

		await self._bot.send_embed_dm(mention, "User Timeout", fields=fields)
		

	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}timeout @user <time> <reason:optional> \
				to timeout a user for a set amount of time and add a strike to their account.", 'inline': False},
			{'name': 'Help2', 'value': f"Use {context.command_character}timeoutns @user <time> <reason:optional> \
				to timeout a user for a set amount of time without adding a strike to their account.", 'inline': False},
			{'name': '<time>', 'value': f"Time allows the following format: <1-2 digit number><one of: s, m, h, d> where \
				s is second, m is minute, h is hour, d is day.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}timeout <@{self._bot.user.id}> 24h Being a bad bot", 'inline': False},
			{'name': 'Note:', 'value': f"if the user has an active timeout already it will extend the duration instead.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Timeout User", fields=fields)

	async def send_no_permission_message(self, context):
		fields = [
			{'name': 'Permission Error', 'value': f"You need to be {self.permission} to execute this command.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "User Timeout", fields=fields)
