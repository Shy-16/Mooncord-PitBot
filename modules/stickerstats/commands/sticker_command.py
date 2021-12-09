# -*- coding: utf-8 -*-

## StickerCommand ##
# A command to show sticker stats. #

from modules.pitbot.commands.context import CommandContext
from modules.pitbot.commands.command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
from log_utils import do_log

class StickerCommand(Command):

	def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(pitbot, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:
		if len(context.params) == 0:
			await self.send_help(context)
			return

		user = None

		# We either need a mention or an ID as first parameter.
		if not context.mentions:
			user_id = context.params[0]
			# review its a "valid" snowflake
			if not len(user_id) > 16:
				await self.send_help(context)
				return

			user = self._pitbot.get_user(user_id=user_id)

			if not user:
				# there is a possibility user is not yet in our database
				user = await self._bot.http.get_user(user_id)

		else:
			user = context.mentions[0]

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'release'}, context=context)

		if not context.is_silent and context.log_channel:
			user_strikes = self._pitbot.get_user_strikes(user, sort=('_id', -1), partial=False)
			user_timeouts = self._pitbot.get_user_timeouts(user=user, status='expired')

			strike_text = "```No Previous Strikes```"
			if len(user_strikes) > 0:
				strike_messages = list()

				for strike in user_strikes[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
					strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{user['id']}> wasn't timed out."
			if timeout_info:
				info_message = f"<@{user['id']}> was released by <@{context.author['id']}>."

			if strike_info:
				info_message += f"\r\n\r\nUser's last strike was deleted."

			fields = [
				{'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
				{'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
				{'name': '\u200B', 'value': strike_text, 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, "Release user", info_message, fields=fields)
