# -*- coding: utf-8 -*-

## Sayo Module ##
# This is the main Bot module with functionality #

import logging
import yaml
import datetime
import discord
from discord.utils import get
from discord.ext import tasks

from db import Database
from .utils import iso_to_datetime, datetime_to_iso, date_string_to_timedelta
from .log_utils import init_log, do_log
from .modules.banwords import Banwords

from .commands import CommandContext, DMContext, Timeout, BotConfig, Release, Strike, Roles, Help, Close, Shutdown

class Sayo(discord.Client):

    def __init__(self, config, args):
        super().__init__(intents=discord.Intents.all())

        if(not args.token):
            print("You need to provide a secret token with \"--token\" or \"-t\" ")
            return

        self.config = config
        self.guild_config = dict()
        self.default_guild = None
        self.args = args
        self.db = Database(self.config['database'])
        self.silent = config['discord']['silent']
        self.banwords = list()
        self.banword_list = list()
        self.banword_module = Banwords(self)

        self.end_bot = False

        self.commands = {
            "shutdown": Shutdown(self, 'admin'),
            "config": BotConfig(self, 'admin'),
            "timeout": Timeout(self, 'mod', ['ban', 'time', 'remaining', 'timeout']),
            "timeoutns": Timeout(self, 'mod', skip_strike=True),
            "release": Release(self, 'mod'),
            "strikes": Strike(self, 'mod', ['strikes', 'pithistory', 'history']),
            "roles": Roles(self, 'mod'),
            "help": Help(self, 'mod', ['help', 'elp'])
        }

        self.commands['ban'] = self.commands['timeout']

        self.dm_commands = {
            "timeout": self.commands['timeout'],
            "strikes": self.commands['strikes'],
            "help": self.commands['help']
        }

        self.ping_commands = {
            "timeout": self.commands['timeout'],
            "ban": self.commands['timeout']
        }

        init_log()

    def run(self):
        self.free_users.start()
        self.refresh_banword_cache.start()
        super().run(self.args.token)

    ### Run Scheduler
    @tasks.loop(seconds=60)
    async def free_users(self):
        if not self.is_ready():
            return

        timeouts = self.db.get_all_timeouts()
        timeouts = list(timeouts)

        for timeout in timeouts:
            issued_date = iso_to_datetime(timeout['created_date'])
            expire_date = issued_date + datetime.timedelta(seconds=timeout['time'])

            user = self.get_user(timeout['user_id'])
            guild = self.get_guild(timeout['guild_id'])
            member = None
            if user is not None:
                member = guild.get_member(user.id)

            if datetime.datetime.now() >= expire_date:
                if user is not None:
                    timeout_info = self.db.remove_user_timeout(user)
                else:
                    timeout_info = self.db.remove_user_timeout(timeout['user_id'])

                if not member:
                    return

                for role in self.guild_config[guild.id]['ban_roles']:
                    await member.remove_roles(guild.get_role(role), reason="Timeout expired.")

                if not self.is_silent(timeout_info['guild_id']):
                    await self.send_embed_message(self.guild_config[guild.id]['log_channel'], "User Released",
                        fields=[{'name': 'Info', 'value': f"User: <@{user.id}> was just released from the pit.", 'inline': False}])

                # Send a DM to the user
                fields = [{'name': 'Timeout', 'value': f"Your timeout in {guild.name} has expired and you've been released from the pit.", 'inline': False},
                    {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                        to get a summary of your disciplinary history on {guild.name}.", 'inline': False}
                ]

                await self.send_embed_dm(member, "User Timeout", fields=fields)

                await do_log(place="auto_task",
                   data_dict={'event': 'auto_release', 'author_id': self.user.id, 'author_handle': f'{self.user.name}#{self.user.discriminator}'},
                   member=member)

    @tasks.loop(seconds=300)
    async def refresh_banword_cache(self):
        if not self.is_ready():
            return

        banwords = self.db.get_banwords()

        self.banwords = list(banwords)
        self.banword_list = [banword['word'] for banword in banwords]

    ### Client Events
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author == self.user or message.author.bot:
            return

        if message.channel.type == discord.enums.ChannelType.private:
            # Someone sent a DM to the bot.
            for dm_command in self.dm_commands:
                for keyword in self.dm_commands[dm_command].dm_keywords:
                    if keyword in message.content:
                        await self.dm_commands[dm_command].dm(DMContext(self, message))
                        return
            return

        command = message.content
        params = message.content.split()

        # Check for pings
        if len(message.mentions) > 0 and message.mentions[0] == self.user:
            # Someone pinged the bot, so lets activate the ping command.
            # We need to make sure that whoever pinged the bot used @sayo as first positional argument
            if len(params) <= 1:
                # we dont care about people just pinging the bot
                return
            
            if params[0] != f'<@!{self.user.id}>':
                # we dont care about people pinging the bot as part of the message
                return

            command = params[1].lower()
            params = params[2:]

            if command in self.ping_commands:
                await self.ping_commands[command].ping(CommandContext(self, command, params, message))
            return

        if message.content.startswith(self.guild_config[message.guild.id]['command_character']):
            command = command.replace(self.guild_config[message.guild.id]['command_character'], '')

            if ' ' in command:
                command, params = (command.split()[0], command.split()[1:])

            command = command.lower()
            
            if command in self.commands:
                await self.commands[command].execute(CommandContext(self, command, params, message))
            return

        # Apply banwords
        #await self.banword_module.handle_message(CommandContext(self, command, params, message))

    async def on_reaction_add(self, reaction, user):
        # This event doesnt trigger if the message is no longer cached
        # Which is fine because we dont want to give users infinite time to create tickets.

        if user == self.user or user.bot:
            return

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        logging.info(f"New bot instance created: {self.user.name} ID: {self.user.id}.")

        print('Loading configuration for guilds:')
        # Load server configuration from database
        for guild in self.guilds:
            print(f'Guild {guild.id} is being loaded.')
            guild_config = self.db.load_server_configuration(guild, self)
            self.guild_config[guild.id] = guild_config
            if self.default_guild is None: self.default_guild = guild_config
            print(f'Guild {guild.id} loaded.')
            logging.info(f"Loaded configuration for guild: {guild.id}.")

        print('Finished loading all guild info.')
        logging.info("All configuration finished.")

        activity = discord.Game("DM to contact staff | DM help for more info.")
        await super().change_presence(activity=activity)

    async def update_guild_configuration(self, guild):
        guild_config = self.db.load_server_configuration(guild, self)
        self.guild_config[guild.id] = guild_config


    # Main 2 events to detect people joining and leaving.
    # These require Intents.Member to be enabled.
    async def on_member_join(self, member):
        # Get timeout info
        timeout = self.db.get_user_timeout(member)

        if timeout:
            # Add a strike to this user.
            self.db.add_strike(member, member.guild, self.user, reason="User rejoined server after leaving during timeout.")
            await do_log(place="bot_events",
                   data_dict={'event': 'member_join', 'author_id': self.user.id, 'author_handle': f'{self.user.name}#{self.user.discriminator}'},
                   member=member)

            if self.guild_config[member.guild.id]['log_channel']:
                await self.send_embed_message(self.guild_config[member.guild.id]['log_channel'], "User Rejoined",
                    fields=[{'name': 'User Rejoined after Timeout', 'value': f"User: <@{member.id}> was timed out, \
                        left the server and joined back again.", 'inline': False}])

            if self.guild_config[member.guild.id]['auto_timeout_on_reenter'] == True:
                for role in self.guild_config[member.guild.id]['ban_roles']:
                    await member.add_roles(member.guild.get_role(role), reason="User rejoined server after leaving during timeout.")

    async def on_member_remove(self, member):
        # Get timeout info
        timeout = self.db.get_user_timeout(member)

        if timeout:
            if self.guild_config[member.guild.id]['log_channel']:
                await self.send_embed_message(self.guild_config[member.guild.id]['log_channel'], "Timeout user left server",
                    fields=[{'name': 'User Left after Timeout', 'value': f"User: <@{member.id}> was timed out and left the server.", 'inline': False}])

            await do_log(place="bot_events",
                   data_dict={'event': 'member_leave', 'author_id': self.user.id, 'author_handle': f'{self.user.name}#{self.user.discriminator}'},
                   member=member)

    # Event to detect changes on roles
    # This also requires Intents.Member
    async def on_member_update(self, before, after):
        '''Before is user previously to change.
        After is user after the change happened.

        Both are Member, not User.'''

        pit_roles = self.guild_config[before.guild.id]['ban_roles']
        timeout = self.db.get_user_timeout(after)

        before_roles = [role.id for role in before.roles]
        after_roles = [role.id for role in after.roles]

        was_pitted = False
        was_released = False

        DEFAULT_TIMEOUT_DURATION = 259200 # 3 days

        for role in pit_roles:
            if role in before_roles and role not in after_roles:
                was_released = True

            elif role in after_roles and role not in before_roles:
                was_pitted = True

        if timeout and was_released:
            timeout_info = self.db.remove_user_timeout(after)

        if not timeout and was_pitted:
            timeout_info = self.db.add_user_timeout(after, after.guild, DEFAULT_TIMEOUT_DURATION, self.user, 'A moderator manually sent this user to the pit.')
            strike_info = self.db.add_strike(after, after.guild, self.user, 'A moderator manually sent this user to the pit.')

            # Maybe send a DM to the user? Waiting for confirmation


    # Register these two just in case
    # These require Intents.bans
    async def on_member_ban(self, guild, user):
        pass

    async def on_member_unban(self, guild, user):
        pass

    ### Utils
    async def send_message(self, channel, message=""):
        if type(channel) is not discord.channel.TextChannel:
            await self.get_channel(channel).send(message)
            return

        new_message = await channel.send(message)
        return new_message

    async def send_embed_message(self, channel, title="", description='', colour=discord.Colour.dark_green(), fields=[], footer=None, footer_icon=discord.Embed.Empty):
        embed = discord.Embed(
            title=title,
            description=description,
            type="rich",
            colour=colour
        )
        for field in fields:
            embed.add_field(name=field['name'],
                            value=field['value'],
                            inline=field['inline'])

        if footer is not None:
            embed.set_footer(text=footer, icon_url=footer_icon)
            
        if type(channel) is not discord.channel.TextChannel:
            await self.get_channel(channel).send("", embed=embed)
            return

        new_message = await channel.send("", embed=embed)
        return new_message

    async def send_dm(self, user, message=""):
        if isinstance(user, int) or isinstance(user, str):
            user = self.get_user(user)

        new_message = await user.send(message)
        return new_message

    async def send_embed_dm(self, user, title="", description='', colour=discord.Colour.dark_green(), fields=[], footer=None, footer_icon=discord.Embed.Empty):
        embed = discord.Embed(
            title=title,
            description=description,
            type="rich",
            colour=colour
        )
        for field in fields:
            embed.add_field(name=field['name'],
                            value=field['value'],
                            inline=field['inline'])

        if footer is not None:
            embed.set_footer(text=footer, icon_url=footer_icon)

        if isinstance(user, int) or isinstance(user, str):
            user = self.get_user(user)

        new_message = await user.send("", embed=embed)
        return new_message

    ### Helpers:
    def is_silent(self, guild_id):
        """Return if silent including config and overrides."""

        if not self.config['discord']['silent'] and not self.guild_config[guild_id]['override_silent']:
                return False

        return True
