# -*- coding: utf-8 -*-

## Bot Module ##
# This is the main Bot module with functionality #

import logging
import discord
import traceback
import random
from typing import Optional

from database import Database
from log_utils import init_log, do_log
from modules import PitBot, Banwords

log: logging.Logger = logging.getLogger("bot")

class Bot(discord.Client):

    def __init__(self, config: dict) -> None:
        super().__init__(intents=discord.Intents.all())

        self.config = config
        self.guild_config = dict()
        self.default_guild = None
        self.silent = config['discord']['silent']

        self.db = Database(config['database'])

        self.pitbot_module = PitBot(bot=self)
        self.banword_module = Banwords(bot=self)

        init_log()

    def run(self, *, token: str) -> None:
        self.pitbot_module.init_tasks()
        self.banword_module.init_tasks()
        super().run(token)

    ## On error handler
    async def on_error(self, event, err):
        exc_err = traceback.format_exc()
        log.error("Bot handled an error on event: {} with error:\r\n{}".format(event, exc_err))

    ### Client Events
    async def on_message_create(self, message: discord.Context) -> None:
        # <Context type=0 tts=False timestamp=2021-11-09T15:32:26.784000+00:00 referenced_message=None pinned=False nonce=907653874028904448 
        # mentions=[] mention_roles=[] mention_everyone=False 
        # member={'roles': ['553482969969459214', ...], 'nick': 'yui', 'mute': False, 'joined_at': '2019-03-08T05:49:16.519000+00:00', 
        # 'hoisted_role': '553454347795824650', 'deaf': False} id=907653873282469888 flags=0 embeds=[] edited_timestamp=None content=test again 
        # components=[] channel_id=593048383405555725 author={'username': 'yuigahamayui', 'public_flags': 128, 'id': '539881999926689829', 
        # 'discriminator': '7441', 'avatar': 'f493550c33cd55aaa0819be4e9a988a6'} attachments=[] guild_id=553454168631934977 event_name=MESSAGE_CREATE>
        #
        # 'attachments', 'author', 'channel_id', 'components', 'content', 'edited_timestamp', 'embeds', 'event_name', 'flags', 'guild_id', 'id', 'member', 
        # 'mention_everyone', 'mention_roles', 'mentions', 'nonce', 'pinned', 'referenced_message', 'timestamp', 'tts', 'type'

        # we do not want the bot to reply to itself
        if int(message.author['id']) == self.user.id or message.author.get('bot', False):
            return

        if not hasattr(message, 'guild_id'):
            # Someone sent a DM to the bot.
            await self.pitbot_module.handle_dm_commands(message)
            return

        # Check for pings
        if len(message.mentions) > 0 and int(message.mentions[0]['id']) == self.user.id:
            # Someone pinged the bot.
            await self.pitbot_module.handle_ping_commands(message)
            return

        if message.content.startswith(self.guild_config[message.guild_id]['command_character']):
            # Someone used a command.
            await self.pitbot_module.handle_commands(message)
            return

        # If none of the above was checked, its a regular message.
        # We pass the message through our banword filter for automatic timeouts.
        await self.banword_module.handle_message(message)

    async def on_ready(self, _) -> None:
        log.info(f"New bot instance created: {self.user.name} ID: {self.user.id}.")

        log.info('Loading configuration for guilds:')
        # Load server configuration from database
        for guild in self.guilds:
            guild_config = self.db.load_server_configuration(guild, self)
            self.guild_config[guild.id] = guild_config
            if self.default_guild is None: self.default_guild = guild_config
            log.info(f"Loaded configuration for guild: {guild.id}.")

        log.info('Finished loading all guild info.')
        log.info("All configuration finished.")

        #activity = discord.Game("DM to contact staff | DM help for more info.")
        #await super().change_presence(activity=activity)

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

    ### Utils
    async def get_guild(self, *, guild_id: int) -> Optional[discord.Guild]:
        """
        Looks for guild information
        """

        guild = next((g for g in self.guilds if g.id == guild_id), None)
        # Optionally maybe get info from discord itself?
        # but for now hard pass since we only work in 1 server.

        return guild

    def get_timeout_image(self):
        """
        Dont ask
        """

        index = random.randint(0, len(self.default_guild['timeout_images']) -1)
        return self.default_guild['timeout_images'][index]

    async def send_message(self, channel_id: int, content: str = "") -> dict:
        message = await self.http.send_message(channel_id, content)
        return message

    async def send_embed_message(self, channel_id: int, title: str = "", description: str = "", color: int = 0x0aeb06, fields: list = list(),
        footer: dict = None, image: dict= None) -> dict:
        embed = {
            "type": "rich",
            "title": title,
            "description": description,
            "color": color,
            "fields": fields
        }

        if footer is not None:
            embed['footer'] = footer

        if image is not None:
            embed['image'] = image

        message = await self.http.send_message(channel_id, '', embed=embed)

        return message

    async def send_dm(self, user_id: int, content: str = "") -> dict:
        dm_channel = await self.http.create_dm(user_id)
        message = await self.http.send_message(dm_channel['id'], content)

        return message

    async def send_embed_dm(self, user_id: int, title: str = "", description: str = "", color: int = 0x0aeb06, fields: list = list(),
        footer: dict = None, image: dict = None) -> dict:

        embed = {
            "type": "rich",
            "title": title,
            "description": description,
            "color": color,
            "fields": fields
        }

        if footer is not None:
            embed['footer'] = footer

        if image is not None:
            embed['image'] = image

        dm_channel = await self.http.create_dm(user_id)
        message = await self.http.send_message(dm_channel['id'], '', embed=embed)

        return message

    ### Helpers:
    def is_silent(self, guild_id) -> bool:
        """Return if silent including config and overrides."""

        if not self.config['discord']['silent'] and not self.guild_config[guild_id]['override_silent']:
                return False

        return True
