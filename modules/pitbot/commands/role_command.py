# -*- coding: utf-8 -*-

## Roles ##
# Roles related commands. #

from modules.context import CommandContext
from modules.command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string

class Roles(Command):

	def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(pitbot, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:
		if len(context.params) == 0:
			await self.send_help(context)
			return

		if not context.mentions:
			await self.send_help(context)
			return

		if not context.role_mentions:
			await self.send_help(context)
			return

		if len(context.params) > 1:

			if context.params[0] == "add":
				await self._do_add_roles(context)
				return

			elif context.params[0] == "rm" or context.params[1] == "remove":
				await self._do_remove_roles(context)
				return

			else:
				await self.send_help(context)
				return

		await self.send_help(context)
		return

	async def send_help(self, context: CommandContext) -> None:
		fields = [
			{'name': 'Help', 'value': f"Use {context.command_character}roles add|rm [@role_1, ...] [@user_1,....] to add all roles to all users.", 'inline': False},
			{'name': 'Additional Info', 'value': f"The list of roles and users must be provided without brackets, \
				just mentioned in the command in any order.", 'inline': False},
			{'name': 'Example', 'value': f"{context.command_character}roles add @GAMEJAM @GAMEDEV <@{self._bot.user.id}>.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Role Updater", fields=fields)

	async def _do_add_roles(self, context: CommandContext) -> None:
		"""
		Adds all specified roles to all specified users
		"""

		for user in context.mentions:
			for role in context.role_mentions:
				await self._bot.http.add_member_role(context.guild.id, user['id'], role, "Requested by a mod.")

		await self._bot.send_embed_message(context.channel_id, "Role Updater", f"{len(context.role_mentions)} roles were added to {len(context.mentions)} users")

	async def _do_remove_roles(self, context: CommandContext) -> None:
		"""
		Removes all specified roles to all specified users
		"""

		for user in context.mentions:
			for role in context.role_mentions:
				await self._bot.http.remove_member_role(context.guild.id, user['id'], role, "Removed by a mod.")

		await self._bot.send_embed_message(context.channel_id, "Role Updater", f"{len(context.role_mentions)} roles were removed from {len(context.mentions)} users")