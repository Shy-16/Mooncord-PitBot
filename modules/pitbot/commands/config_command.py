# -*- coding: utf-8 -*-

## Config ##
# Manage Guild Configuration. #

from modules.context import CommandContext
from modules.command import Command, verify_permission

class BotConfig(Command):

	def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(pitbot, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:
		if len(context.params) == 0:
			# Show current server config
			await self._show_server_configuration(context)
			return

		if len(context.params) <= 2:
			await self.send_help(context)
			return

		if 'banword' in context.params[1]:
			await self.send_banwords(context)
			return

		if context.params[0] == "set":

			if context.params[1] == "log_channel":
				await self._set_log_channel(context)

			elif context.params[1] == "override_silent":
				await self._set_override_silent(context)

			elif context.params[1] == "command_character":
				await self._set_command_character(context)

		elif context.params[0] == "add":

			if 'role' in context.params[1]:
				await self._add_role(context)

		elif context.params[0] == "rm" or context.params[0] == "remove":

			if 'role' in context.params[1]:
				await self._remove_role(context)


	async def send_banwords(self, context: CommandContext) -> None:
		fields = [
			{'name': 'Banwords', 'value': f"Please use the website to configure banwords.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel, "Server Configuration", fields=fields)

	async def send_help(self, context: CommandContext) -> None:
		description = f"Use {context.command_character}config set|add|rm <name> <value> \
				to set a new value or add/remove a value from an array."

		await self._bot.send_embed_message(context.channel, "Server Configuration", description)

	# Private functions
	async def _show_server_configuration(self, context: CommandContext) -> None:
		guild_config = self._bot.guild_config[context.guild.id]

		admin_role_text = []
		for role in guild_config['admin_roles']:
			admin_role_text.append(f"- <@&{role}>")
		admin_text = '\r\n'.join(admin_role_text)
		if admin_text == '': admin_text = 'No admin roles specified.'

		mod_role_text = []
		for role in guild_config['mod_roles']:
			mod_role_text.append(f"- <@&{role}>")
		mod_text = '\r\n'.join(mod_role_text)
		if mod_text == '': mod_text = 'No mod roles specified.'

		ban_role_text = []
		for role in guild_config['ban_roles']:
			ban_role_text.append(f"- <@&{role}>")
		ban_text = '\r\n'.join(ban_role_text)
		if ban_text == '': ban_text = 'No ban roles specified.'

		sub_role_text = []
		for role in guild_config['sub_roles']:
			sub_role_text.append(f"- <@&{role}>")
		sub_text = '\r\n'.join(sub_role_text)
		if sub_text == '': sub_text = 'No sub roles specified.'

		log_channel = "No channel configured"
		if guild_config['log_channel']:
			log_channel = f"<#{guild_config['log_channel']}>"

		fields = [
			{'name': 'Help', 'value': f"Use {guild_config['command_character']}config set|add|rm <name> <value> \
				to set a new value or add/remove a value from an array.", 'inline': False},
			{'name': 'command_character', 'value': f"{guild_config['command_character']}", 'inline': False},
			#{'name': 'allowed_channels', 'value': f"{guild_config['allowed_channels']}", 'inline': False},
			#{'name': 'denied_channels', 'value': f"{guild_config['denied_channels']}", 'inline': False},
			{'name': 'admin_roles', 'value': f"{admin_text}", 'inline': False},
			{'name': 'mod_roles', 'value': f"{mod_text}", 'inline': False},
			{'name': 'ban_roles', 'value': f"{ban_text}", 'inline': False},
			{'name': 'sub_roles', 'value': f"{sub_text}", 'inline': False},
			{'name': 'banwords', 'value': f"Use the website to configure banwords.", 'inline': False},
			{'name': 'log_channel', 'value': f"{log_channel}", 'inline': False},
			{'name': 'override_silent', 'value': f"{guild_config['override_silent']}", 'inline': False},
			{'name': 'auto_timeout_on_reenter', 'value': f"{guild_config['auto_timeout_on_reenter']}", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, f"{guild_config['name']} Config", fields=fields)

	async def _set_log_channel(self, context: CommandContext) -> None:
		if context.channel_mentions:
			channel_id = context.channel_mentions[0]

			guild_config = self._bot.db.update_server_configuration(context.guild, {'log_channel': channel_id})
			await self._bot.update_guild_configuration(context.guild)

			fields= [
				{'name': 'log_channel', 'value': f"Log Channel was properly set up to: <#{context.channel_mentions[0]}>", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)

		else:
			fields= [
				{'name': 'log_channel', 'value': f"You need to mention a channel. Ex: `{guild_config['command_character']}config \
					set log_channel #channel_mention`", 'inline': False}
			]
			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)

	async def _set_override_silent(self, context: CommandContext) -> None:
		value = params[2].lower in ["true", "yes", "1"]

		guild_config = self._bot.db.update_server_configuration(context.guild, {'override_silent': value})
		await self._bot.update_guild_configuration(context.guild)

		fields= [
			{'name': 'override_silent', 'value': f"Override silent was properly set to: {value}", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)

	async def _set_command_character(self, context: CommandContext) -> None:
		value = context.params[2]

		if value is None or value == '':
			fields= [
				{'name': 'command_character', 'value': "Command Character cannot be empty.", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)
			return

		guild_config = self._bot.db.update_server_configuration(context.guild, {'command_character': value})
		await self._bot.update_guild_configuration(context.guild)

		fields= [
			{'name': 'command_character', 'value': f"Command characters was properly set to: {value}. Make sure it doesn't conflict with other bots.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)

	async def _add_role(self, context: CommandContext) -> None:
		which = context.params[1]

		if which not in ['admin_roles', 'mod_roles', 'ban_roles', 'sub_roles']:
			fields= [
				{'name': 'add *_roles', 'value': f"Available lists are: `admin_roles`, `mod_roles`, `ban_roles`, `sub_roles`", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)
			return

		if not context.role_mentions:
			fields= [
				{'name': 'add *_roles', 'value': f"You need to tag at least one role. \
					Ex: {context.command_character}config add admin_roles @AwesomeAdminRole", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)
			return

		role = context.role_mentions[0]

		guild_info = self._bot.db.add_role_to_guild(context.guild, which, role)
		await self._bot.update_guild_configuration(context.guild)

		fields= [
			{'name': f'add {which}', 'value': f"<@&{role}> ({role}) was properly added to server config.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)

	async def _remove_role(self, context: CommandContext) -> None:
		which = context.params[1]

		if which not in ['admin_roles', 'mod_roles', 'ban_roles', 'sub_roles']:
			fields= [
				{'name': 'add *_roles', 'value': f"Available lists are: `admin_roles`, `mod_roles`, `ban_roles`, `sub_roles`", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)
			return

		if not context.role_mentions:
			fields= [
				{'name': 'add *_roles', 'value': f"You need to tag at least one role. \
					Ex: {context.command_character}config add admin_roles @AwesomeAdminRole", 'inline': False}
			]

			await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)
			return

		role = context.role_mentions[0]

		guild_info = self._bot.db.remove_role_from_guild(context.guild, which, role)
		await self._bot.update_guild_configuration(context.guild)

		fields= [
			{'name': f'add {which}', 'value': f"<@&{role}> ({role}) was properly removed from server config.", 'inline': False}
		]

		await self._bot.send_embed_message(context.channel_id, "Server Configuration", fields=fields)