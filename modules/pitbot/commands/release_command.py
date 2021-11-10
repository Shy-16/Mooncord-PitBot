# -*- coding: utf-8 -*-

## Timeout ##
# A command to timeout people. #

from .command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
from log_utils import do_log

class Release(Command):

	def __init__(self, bot, permission='mod'):
		"""
		@bot: Sayo
		@permission: A minimum allowed permission to execute command.
		"""
		super().__init__(bot, permission)

	@verify_permission
	async def execute(self, context):
		if len(context.params) == 0:
			await self.send_help(context)
			return

		if not context.mentions:
			# Mentions can be empty if the tagged user is not in the server anymore.
			if not '<@' in context.params[0]:
				await self.send_help(context)
				return

			await self.execute_user_left_server(context)
			return

		else:
			mention = context.mentions[0]

		amend = False
		if len(context.params) > 1:
			if context.params[1].lower() == "amend":
				amend = True

		for role in context.ban_roles:
			await mention.remove_roles(context.guild.get_role(role), reason="Timeout released by a mod.")
		timeout_info = self._bot.db.remove_user_timeout(mention)
		if amend:
			strike_info = self._bot.db.delete_strike(mention, context.guild)

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'release'}, message=context.message)

		if not context.is_silent and context.log_channel:

			user_timeouts = self._bot.db.get_user_timeouts(mention, {'status': 'expired'})
			user_strikes = self._bot.db.get_user_strikes(mention)

			strike_text = ""
			if user_strikes.count() > 0:
				strike_messages = list()

				for strike in user_strikes.sort('_id', -1)[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = context.guild.get_member(strike['issuer_id'])
					strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason']} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			if timeout_info is None:
				timeout_message = f"<@{mention.id}> wasn't Timed out."
			else:
				timeout_message = f"<@{mention.id}> was released by <@{context.author.id}>."

			fields = [
				{'name': 'Issue', 'value': timeout_message, 'inline': False},
				{'name': 'Strikes', 'value': f"<@{mention.id}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "User Timeout", fields=fields)

	async def execute_user_left_server(self, context):
		class MockMember:
			def __init__(self, _id):
				self.id = _id

		mention = MockMember(context.params[0][2:-1])

		amend = False
		if len(context.params) > 1:
			if context.params[1].lower() == "amend":
				amend = True

		timeout_info = self._bot.db.remove_user_timeout(mention)
		if amend:
			strike_info = self._bot.db.delete_strike(mention, context.guild)

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'release'}, message=context.message)

		if not context.is_silent and context.log_channel:

			user_timeouts = self._bot.db.get_user_timeouts(mention, {'status': 'expired'})
			user_strikes = self._bot.db.get_user_strikes(mention)

			strike_text = ""
			if user_strikes.count() > 0:
				strike_messages = list()

				for strike in user_strikes.sort('_id', -1)[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = context.guild.get_member(strike['issuer_id'])
					strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason']} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			if timeout_info is None:
				timeout_message = f"<@{mention.id}> wasn't Timed out."
			else:
				timeout_message = f"<@{mention.id}> was released by <@{context.author.id}>."

			fields = [
				{'name': 'Issue', 'value': timeout_message, 'inline': False},
				{'name': 'Strikes', 'value': f"<@{mention.id}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "User Timeout", fields=fields)


	async def send_help(self, context):
		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}release @user <amend:optional> will release a user from an active timeout.", 'inline': False},
			{'name': '<amend>', 'value': f"If `amend` is provided after user ping, it will delete the last strike issued from a Timeout.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}release <@{self._bot.user.id}> amend", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Release User", fields=fields)

	async def send_no_permission_message(self, context):
		fields = [
			{'name': 'Permission Error', 'value': f"You need to be {self.permission} to execute this command.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Release User", fields=fields)
