# -*- coding: utf-8 -*-

## Strike ##
# Strike related commands. #

from .command import Command, verify_permission
from bot.utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
from bot.log_utils import do_log

class Strike(Command):

	def __init__(self, bot, permission='mod', dm_keywords=list()):
		"""
		@bot: Sayo
		@permission: A minimum allowed permission to execute command.
		"""
		super().__init__(bot, permission, dm_keywords)

	@verify_permission
	async def execute(self, context):
		if len(context.params) == 0:
			await self.send_help(context)
			return

		if not context.mentions:
			await self.send_help(context)
			return

		if len(context.params) > 1:

			if context.params[1] == "add":
				await self._do_add_strike(context)
				return

			elif context.params[1] == "rm" or context.params[1] == "remove":
				await self._do_remove_strike(context)
				return

			elif context.params[1] == "verbose":
				await self._do_show_strike(context, verbose=True)
				return

			else:
				await self.send_help(context)
				return

		await self._do_show_strike(context)
		return

	async def dm(self, context):

		user_strikes = self._bot.db.get_all_user_strikes(context.author)

		active_strike_text = ""
		expired_strike_text = ""

		if user_strikes.count() > 0:
			active_strike_messages = list()
			expired_strike_messages = list()

			for strike in user_strikes.sort('_id', -1):
				date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
				if strike['status'] == 'active':
					active_strike_messages.append(f"{date} - Striked for {strike['reason']}")
				else:
					expired_strike_messages.append(f"{date} - Striked for {strike['reason']}")

			active_strike_text = "```" + "\r\n".join(active_strike_messages) + "```" if len(active_strike_messages) > 0 else '```No active strikes```'
			expired_strike_text = "```" + "\r\n".join(expired_strike_messages) + "```" if len(expired_strike_messages) > 0 else '```No previous strikes```'

			fields = [
				{'name': 'Info', 'value': f"You have {len(active_strike_messages)} active strikes.", 'inline': False},
				{'name': 'Active Strikes', 'value': f"{active_strike_text}", 'inline': False},
				{'name': 'Previous Strikes', 'value': f"{expired_strike_text}", 'inline': False}
			]

			await self._bot.send_embed_dm(context.author, "User Strikes", fields=fields)

		else:

			fields = [
				{'name': 'Info', 'value': f"You don't have any active strikes.", 'inline': False}
			]

			await self._bot.send_embed_dm(context.author, "User Strikes", fields=fields)

		await do_log(place="dm", data_dict={'event': 'command', 'command': 'strikes', 'author_id': context.author.id,
				   			  'author_handle': f'{context.author.name}#{context.author.discriminator}'})

	async def send_help(self, context):
		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}strikes @user <verbose:optional> to get all strikes a user has.", 'inline': False},
			{'name': 'Add', 'value': f"Use {context.command_character}strikes @user add <reason:optional> to add a strike to a user.", 'inline': False},
			{'name': 'Remove', 'value': f"Use {context.command_character}strikes @user rm <strike_id> to remove a strike from a user.\r\n" +
				"<strike_id> is the UniqueID provided on the list of strikes of the user, which uniquely identify each strike.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}strikes <@{self._bot.user.id}> add Too dumb.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "User Strikes", fields=fields)

	async def send_no_permission_message(self, context):
		fields = [
			{'name': 'Permission Error', 'value': f"You need to be {self.permission} to execute this command.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "User Timeout", fields=fields)

	async def _do_show_strike(self, context, verbose=False):
		mention = context.mentions[0]

		if not verbose:
			user_strikes = self._bot.db.get_user_strikes(mention)

			fields = [
				{'name': 'Strikes', 'value': f"<@{mention.id}> has {user_strikes.count()} active strikes.", 'inline': False}
			]
			await self._bot.send_embed_message(context.log_channel, "User Strikes", fields=fields)
			await do_log(place="guild", data_dict={'event': 'command', 'command': 'show_strikes'}, message=context.message)
			return

		user_strikes = self._bot.db.get_all_user_strikes(mention)

		active_strike_text = ""
		expired_strike_text = ""
		if user_strikes.count() > 0:
			active_strike_messages = list()
			expired_strike_messages = list()

			for strike in list(user_strikes.sort('_id', -1))[0:5]:
				date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
				issuer = context.guild.get_member(strike['issuer_id'])
				if strike['status'] == 'active':
					active_strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason'][0:90]} - {strike['_id']}")
				else:
					expired_strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason'][0:90]} - {strike['_id']}")

			active_strike_text = "```" + "\r\n".join(active_strike_messages) + "```" if len(active_strike_messages) > 0 else '```No active strikes```'
			expired_strike_text = "```" + "\r\n".join(expired_strike_messages) + "```" if len(expired_strike_messages) > 0 else '```No previous strikes```'

		fields = [
			{'name': 'Info', 'value': f"<@{mention.id}> has {user_strikes.count()} previous strikes.", 'inline': False},
			{'name': 'Active Strikes', 'value': f"{active_strike_text}", 'inline': False},
			{'name': 'Previous Strikes', 'value': f"{expired_strike_text}", 'inline': False}
		]

		await self._bot.send_embed_message(context.log_channel, "User Strikes", fields=fields)
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'show_strikes'}, message=context.message)

	async def _do_add_strike(self, context):
		mention = context.mentions[0]

		reason = 'No reason specified'
		if len(context.params) >= 2:
			reason = ' '.join(context.params[2:])

		strike_info = self._bot.db.add_strike(mention, context.guild, context.author, reason)
		user_strikes = self._bot.db.get_user_strikes(mention)

		strike_text = ""
		if user_strikes.count() > 0:
			strike_messages = list()

			for strike in user_strikes.sort('_id', -1)[:5]:
				date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
				issuer = context.guild.get_member(strike['issuer_id'])
				strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason']} - {strike['_id']}")

			strike_text = "```" + "\r\n".join(strike_messages) + "```"

		fields= [
			{'name': 'Info', 'value': f"A strike was added to user: <@{mention.id}>", 'inline': False},
			{'name': 'Strikes', 'value': f"<@{mention.id}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "User Strikes", fields=fields)
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'add_strikes'}, message=context.message)

	async def _do_remove_strike(self, context):
		mention = context.mentions[0]

		if len(context.params) < 2:
			await self._do_add_strike(context)
			return

		strike_id = context.params[2]

		strike_info = self._bot.db.remove_strike(mention, context.guild, strike_id)
		if strike_info is None:
			fields= [
				{'name': 'Info', 'value': f"The strike wasn't found or couldn't be removed.", 'inline': False},
			]

			await self._bot.send_embed_message(context.channel, "User Strikes", fields=fields)
			return

		user_strikes = self._bot.db.get_user_strikes(mention)

		strike_text = ""
		if user_strikes.count() > 0:
			strike_messages = list()

			for strike in user_strikes.sort('_id', -1)[:5]:
				date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
				issuer = context.guild.get_member(strike['issuer_id'])
				strike_messages.append(f"{date} Strike by {issuer.display_name} for {strike['reason']} - {strike['_id']}")

			strike_text = "```" + "\r\n".join(strike_messages) + "```"

		fields= [
			{'name': 'Info', 'value': f"A strike was removed from user: <@{mention.id}>", 'inline': False},
			{'name': 'Strikes', 'value': f"<@{mention.id}> has {user_strikes.count()} active strikes:\r\n{strike_text}", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "User Strikes", fields=fields)
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'remove_strikes'}, message=context.message)