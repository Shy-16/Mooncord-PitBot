# -*- coding: utf-8 -*-

## Close ##
# A command to close modmail tickets. #

from .command import Command, verify_permission
from bot.log_utils import do_log

class Close(Command):

	def __init__(self, bot, modmail, permission='mod', dm_keywords=list()):
		"""
		@bot: Sayo
		@modmail: modmail module
		@permission: A minimum allowed permission to execute command.
		"""
		super().__init__(bot, permission, dm_keywords)

		self.modmail = modmail

	@verify_permission
	async def execute(self, context):
		await self.modmail.close_ticket(context)
		
		await do_log(place="guild", data_dict={'event': 'command', 'command': 'timeout'}, message=context.message)

	async def send_help(self, context):
		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}close <reason:optional> to close a modmail ticket.", 'inline': False},
			{'name': '<reason>', 'value': f"A reason for closing the ticket. If none is given 'No reason given' will be used by default.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}close 610011803020e5b9cc0c6f0d using bot to meme spam", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Close Ticket", fields=fields)

	async def send_no_permission_message(self, context):
		fields = [
			{'name': 'Permission Error', 'value': f"You need to be {self.permission} to execute this command.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Close Ticket", fields=fields)
