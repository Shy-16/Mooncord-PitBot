# -*- coding: utf-8 -*-

## Command Context ##
# Loads all context required to execute commands #

import re

import discord

class ApplicationCommandContext:

    CHANNEL_MENTION_PATTERN = r"\<\#([0-9]+)[>]"

    def __init__(self, bot: discord.Client, context: str) -> None:
        # context: 'application_id', 'channel_id', 'data', 'guild_id', 'id', 'member', 'send', 'token', 'type', 'version'
        self._bot = bot
        self.context = context

        self.id = context.id
        self.application_id = context.application_id
        self.channel_id = context.channel_id

        self.data = context.data
        self.options = list()
        self.options_dict = dict()

        if "options" in context.data:
            # 'options': [{'value': '2d', 'type': 3, 'name': 'time'}]
            self.options = context.data['options']
            for option in self.options:
                self.options_dict[option['name']] = option['value']

        self.options_mention = dict()
        if "resolved" in context.data:
            # resolved is a dict which has 'members' and 'users' as keys which are dicts with the ID as a key
            for key in context.data['resolved']['members']:
                self.options_mention[key] = {**context.data['resolved']['members'][key], **context.data['resolved']['users'][key]}

        self.guild_id = context.guild_id
        self.guild = next((g for g in bot.guilds if g.id == context.guild_id), None)

        self.member = context.member
        self.user = context.member['user']
        self.member.update(self.user) # ease of use
        
        self.token = context.token
        self.type = context.type
        self.version = context.version

        #self.mentions = context.mentions # list of objects
        #self.role_mentions = context.mention_roles # list of IDs
        #self.channel_mentions = re.findall(self.CHANNEL_MENTION_PATTERN, context.content) # list of IDs

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
