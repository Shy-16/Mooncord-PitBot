# -*- coding: utf-8 -*-

## Command Context ##
# Loads all context required to execute commands #

import discord


class CommandContext:
    def __init__(self, bot: discord.Bot, command: str, params: list, message: discord.Message) -> None:
        self._bot = bot
        self.command = command
        self.params = params
        self.message = message
        self.content = self.message.content

        self.id = message.id
        self.author = message.author
        self.guild = message.guild
        self.channel = message.channel
        self.channel_id = message.channel.id

        self.mentions = message.mentions
        self.role_mentions = message.role_mentions
        self.channel_mentions = message.channel_mentions

        self.stickers = message.stickers

        self.is_admin = self._is_admin()
        self.is_mod = self._is_mod()
        self.is_silent = self._bot.is_silent(self.guild.id)
        self.log_channel = int(self._bot.guild_config[self.guild.id]['log_channel'])
        self.command_character = self._bot.guild_config[self.guild.id]['command_character']
        self.ban_roles = [discord.Object(int(role)) for role in self._bot.guild_config[self.guild.id]['ban_roles']]

    def _is_admin(self):
        """Check all roles for admin privileges"""
        return any(str(role.id) in self._bot.guild_config[self.guild.id]['admin_roles'] for role in self.author.roles)

    def _is_mod(self):
        """Check all roles for mod privileges"""
        return any(str(role.id) in self._bot.guild_config[self.guild.id]['mod_roles'] for role in self.author.roles)



class DMContext:
    def __init__(self, bot: discord.Bot, message: discord.Message) -> None:
        self._bot = bot
        self.message = message

        self.author = message.author
        self.channel = message.channel
        self.channel_id = message.channel.id
        self.mentions = message.mentions
        self.channel_mentions = message.channel_mentions

        self.log_channel = self._bot.default_guild['log_channel']
        self.command_character = self._bot.default_guild['command_character']


class InteractionContext:
    def __init__(self, bot: discord.AutoShardedBot, interaction: discord.Interaction) -> None:
        self._bot = bot
        self.message = interaction.message
        self.content = self.message.content

        self.id = self.message.id
        self.author = self.message.author
        self.guild = self.message.guild
        self.channel = self.message.channel
        self.channel_id = self.message.channel.id

        self.is_admin = self._is_admin()
        self.is_mod = self._is_mod()
        self.is_silent = self._bot.is_silent(self.guild.id)
        self.log_channel = int(self._bot.guild_config[self.guild.id]['log_channel'])
        self.command_character = self._bot.guild_config[self.guild.id]['command_character']
        self.ban_roles = [discord.Object(int(role)) for role in self._bot.guild_config[self.guild.id]['ban_roles']]

    def _is_admin(self):
        """Check all roles for admin privileges"""
        return any(str(role.id) in self._bot.guild_config[self.guild.id]['admin_roles'] for role in self.author.roles)

    def _is_mod(self):
        """Check all roles for mod privileges"""
        return any(str(role.id) in self._bot.guild_config[self.guild.id]['mod_roles'] for role in self.author.roles)
