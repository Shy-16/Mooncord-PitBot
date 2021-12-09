# -*- coding: utf-8 -*-

## StickerCommand ##
# A command to show sticker stats. #

from modules.pitbot.commands.context import CommandContext
from modules.pitbot.commands.command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
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
			sticker = self._pitbot.get_sticker(sticker_id=context.sticker_items[0]['id'])

		else:
			if context.params[0].isdigit():
				sticker = self._pitbot.get_sticker(sticker_id=context.params[0])
			else:
				sticker = self._pitbot.get_sticker(name=context.params[0])

		await do_log(place="guild", data_dict={'event': 'command', 'command': 'stickers'}, context=context)

		if not context.is_silent and context.log_channel:
			sticker_text = "```Sticker hasn't been used in any channels.```"

			if len(sticker['channels']) > 0:
				sticker_messages = list()

				for channel, count in sticker['channels'].items():
					sticker_messages.append(f"{channel}: {count} times")

				sticker_text = "```" + "\r\n".join(sticker_messages) + "```"

			info_message = 'Sticker has been used a total of {} times'.format(sum([sticker['channels'][channel] for channel in sticker['channels']]))

			fields = [
				{'name': '\u200B', 'value': sticker_text, 'inline': False}
			]

			await self._bot.send_embed_message(context.log_channel, sticker['name'], info_message, fields=fields)

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