# -*- coding: utf-8 -*-

## Command Context ##
# Loads all context required to execute commands #


class CommandContext:

	def __init__(self, bot, command, params, message):
		self._bot = bot
		self.command = command
		self.params = params
		self.message = message

		self.author = message.author
		self.guild = message.guild

		self.channel = message.channel
		self.mentions = message.mentions
		self.channel_mentions = message.channel_mentions
		self.role_mentions = message.role_mentions

		self.is_admin = self._is_admin()
		self.is_mod = self._is_mod()

		self.is_silent = self._bot.is_silent(self.guild.id)
		self.log_channel = self._bot.guild_config[self.guild.id]['log_channel']
		self.modmail_channel =  self._bot.guild_config[self.guild.id].get('modmail_channel')
		if not self.modmail_channel: self.modmail_channel = self.log_channel
		self.command_character = self._bot.guild_config[self.guild.id]['command_character']

		self.ban_roles = self._bot.guild_config[self.guild.id]['ban_roles']

	def _is_admin(self):
		"""Check all roles for admin privileges"""

		for role in self.message.author.roles:
			if role.id in self._bot.guild_config[self.guild.id]['admin_roles']:
				return True

		return False

	def _is_mod(self):
		"""Check all roles for mod privileges"""

		for role in self.message.author.roles:
			if role.id in self._bot.guild_config[self.guild.id]['mod_roles']:
				return True

		return False

class DMContext:

	def __init__(self, bot, message):
		self._bot = bot
		self.message = message

		self.author = message.author

		self.channel = message.channel
		self.mentions = message.mentions
		self.channel_mentions = message.channel_mentions

		self.log_channel = self._bot.default_guild['log_channel']
		self.modmail_channel =  self._bot.default_guild.get('modmail_channel')
		if not self.modmail_channel: self.modmail_channel = self.log_channel