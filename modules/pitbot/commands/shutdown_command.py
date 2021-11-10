# -*- coding: utf-8 -*-

## Timeout ##
# A command to timeout people. #

from .command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
from log_utils import do_log

class Shutdown(Command):

	def __init__(self, bot, permission='admin'):
		"""
		@bot: Sayo
		@permission: A minimum allowed permission to execute command.
		"""
		super().__init__(bot, permission)

	@verify_permission
	async def execute(self, context):
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'shutdown'}, message=context.message)

		fields = [
			{'name': 'Info', 'value': f'Shutting down issued by <@{context.author.id}>.\r\nYou need to start me again from command line.', 'inline': False},
		]

		await self._bot.send_embed_message(context.log_channel, "Shutdown", fields=fields)

		self._bot.end_bot = True
		await self._bot.close()


	async def send_help(self, context):
		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}shutdown to kill the bot.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}shutdown", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Shutdown", fields=fields)

	async def send_no_permission_message(self, context):
		fields = [
			{'name': 'Permission Error', 'value': f"You need to be {self.permission} to execute this command.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Shutdown", fields=fields)
