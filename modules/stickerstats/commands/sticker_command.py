# -*- coding: utf-8 -*-

## StickerCommand ##
# A command to show sticker stats. #

from modules.context import CommandContext
from modules.command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string, take
from log_utils import do_log

class StickerCommand(Command):

	def __init__(self, stickerstats, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(stickerstats, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:

		sticker = None

		if len(context.sticker_items) <= 0 and len(context.params) <= 0:
			await self.send_help(context)
			return

		if len(context.sticker_items) > 0:
			sticker = self._module.get_sticker(sticker_id=context.sticker_items[0]['id'])

		else:
			if context.params[0].isdigit():
				sticker = self._module.get_sticker(sticker_id=context.params[0])
			else:
				sticker = self._module.get_sticker(name=context.params[0])

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'stickers'}, context=context)

		if not context.is_silent and context.log_channel:
			sticker_text = "```Sticker hasn't been used in any channels.```"

			if len(sticker['channels']) > 0:
				sticker_messages = list()

				for channel, count in take(5, dict(sorted(sticker['channels'].items(), key=lambda item: item[1], reverse=True)).items()):
					sticker_messages.append(f"<#{channel}>: {count} times")

				sticker_text = "\r\n".join(sticker_messages)

			info_message = 'Sticker was created <t:{}:f>\r\nIt has been used a total of {} times'.format(
					int(iso_to_datetime(sticker['created_date']).timestamp()), 
					sum([sticker['channels'][channel] for channel in sticker['channels']])
				)

			fields = [
				{'name': '\u200B', 'value': sticker_text, 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, sticker['name'], info_message, fields=fields)

	async def send_help(self, context: CommandContext) -> None:
		"""
		Sends Help information to the channel
		"""

		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}sticker <id:optional>|<name:optional> \
				to get stats about sticker usage.", 'inline': False},
			{'name': 'Help2', 'value': f"You need to provide either a sticker ID, a sticker Name or \
				simply attach a sticker to the command.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}sticker GAGAGA", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Sticker Stats", fields=fields)