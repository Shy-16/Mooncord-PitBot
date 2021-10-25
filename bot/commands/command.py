# -*- coding: utf-8 -*-

## Command ##
# A reusable Command class to execute functionality with ease #


class Command:

	def __init__(self, bot, permission='mod', dm_keywords=list()):
		"""
		@bot: Sayo
		@permissions: A minimum allowed permission to execute command.
		"""
		self._bot = bot
		self.permission = permission
		self.dm_keywords = dm_keywords

	async def execute(self, context):
		# Takes CommandContext and executes functionality
		pass

	async def dm(self, context):
		# Responds to a user DM of this command
		pass

	async def ping(self, context):
		# Responde to a user pinging the bot
		pass

	async def send_help(self, context):
		# Prints the help command
		pass

	async def send_no_permission_message(self, context):
		pass

def verify_permission(fn):
	async def inner(*args,**kwargs):
		command, context = args

		if command.permission == 'admin':
			if not context.is_admin:

				#if not context.is_silent:
				#	await command.send_no_permission_message(context)

				return

		elif command.permission == 'mod':
			if not (context.is_mod or context.is_admin):

				#if not context.is_silent:
				#	await command.send_no_permission_message(context)

				return

		await fn(*args,**kwargs)

		return
	return inner
