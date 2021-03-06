# -*- coding: utf-8 -*-

## Command Context ##
# Loads all context required to execute commands #

import re

import discord

class CommandContext:

	CHANNEL_MENTION_PATTERN = r"\<\#([0-9]+)[>]"

	def __init__(self, bot: discord.Client, command: str, params: str, context: discord.Context) -> None:
		self._bot = bot
		self.command = command
		self.params = params
		self.content = context.content
		self.context = context

		self.id = context.id
		self.author = context.author
		self.member = context.member
		self.guild = next((g for g in bot.guilds if g.id == context.guild_id), None)
		self.channel_id = context.channel_id

		# mentions=[{'username': 'MEE6', 'public_flags': 65536, 'member': {'roles': ['553455586709078024', '553455365233311765'], 'mute': False, 
        # 'joined_at': '2019-03-08T05:54:01.336000+00:00', 'hoisted_role': '553455586709078024', 'deaf': False}, 'id': '159985870458322944', 'discriminator': '4876', 
        # 'bot': True, 'avatar': 'b50adff099924dd5e6b72d13f77eb9d7'}] mention_roles=['553455365233311765']
		self.mentions = context.mentions # list of objects
		self.role_mentions = context.mention_roles # list of IDs
		self.channel_mentions = re.findall(self.CHANNEL_MENTION_PATTERN, context.content) # list of IDs


		self.sticker_items = list()
		if hasattr(context, 'sticker_items'):
			self.sticker_items = context.sticker_items

		self.is_admin = self._is_admin()
		self.is_mod = self._is_mod()

		self.is_silent = self._bot.is_silent(self.guild.id)
		self.log_channel = self._bot.guild_config[self.guild.id]['log_channel']
		self.command_character = self._bot.guild_config[self.guild.id]['command_character']

		self.ban_roles = self._bot.guild_config[self.guild.id]['ban_roles']

	def _is_admin(self):
		"""Check all roles for admin privileges"""

		for role in self.context.member['roles']:
			if role in self._bot.guild_config[self.guild.id]['admin_roles']:
				return True

		return False

	def _is_mod(self):
		"""Check all roles for mod privileges"""

		for role in self.context.member['roles']:
			if role in self._bot.guild_config[self.guild.id]['mod_roles']:
				return True

		return False

class DMContext:

	CHANNEL_MENTION_PATTERN = r"\<\#([0-9]+)[>]"

	def __init__(self, bot, context):
		self._bot = bot
		self.context = context

		self.author = context.author

		self.channel_id = context.channel_id
		self.mentions = context.mentions # list of objects
		self.channel_mentions = re.findall(self.CHANNEL_MENTION_PATTERN, context.content) # list of IDs

		self.log_channel = self._bot.default_guild['log_channel']
		self.command_character = self._bot.default_guild['command_character']
