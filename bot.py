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
from modules import PitBot, Banwords, StickerStats, Roulette
from application_commands import (
    set_help_slash,
    set_selfpit_slash,
    set_timeout_slash,
    set_timeoutns_slash,
    set_release_slash
)

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
        self.sticker_module = StickerStats(bot=self)
        self.roulette_module = Roulette(bot=self)

        init_log()

        set_help_slash(self)
        set_selfpit_slash(self)

    def run(self, *, token: str) -> None:
        self.pitbot_module.init_tasks()
        self.banword_module.init_tasks()
        self.roulette_module.init_tasks()
        super().run(token)

    ## On error handler
    async def on_error(self, event, err):
        exc_err = traceback.format_exc()
        log.error("Bot handled an error on event: {} with error:\r\n{}".format(event, exc_err))

    ### Client Events
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

        # Setup role-based commands
        set_timeout_slash(self)
        set_timeoutns_slash(self)
        set_release_slash(self)

        #activity = discord.Game("DM to contact staff | DM help for more info.")
        #await super().change_presence(activity=activity)

    async def on_message_create(self, message: discord.Context) -> None:
        # <Context type=0 tts=False timestamp=2021-11-09T15:32:26.784000+00:00 referenced_message=None pinned=False nonce=907653874028904448 
        # mentions=[] mention_roles=[] mention_everyone=False 
        # member={'roles': ['553482969969459214', ...], 'nick': 'yui', 'mute': False, 'joined_at': '2019-03-08T05:49:16.519000+00:00', 
        # 'hoisted_role': '553454347795824650', 'deaf': False} id=907653873282469888 flags=0 embeds=[] edited_timestamp=None content=test again 
        # components=[] channel_id=593048383405555725 author={'username': 'yuigahamayui', 'public_flags': 128, 'id': '539881999926689829', 
        # 'discriminator': '7441', 'avatar': 'f493550c33cd55aaa0819be4e9a988a6'} attachments=[] guild_id=553454168631934977 event_name=MESSAGE_CREATE>
        # sticker_items=[{'name': 'GAGAGAGA', 'id': '915657255309942836', 'format_type': 2}]
        #
        # 'attachments', 'author', 'channel_id', 'components', 'content', 'edited_timestamp', 'embeds', 'event_name', 'flags', 'guild_id', 'id', 'member', 
        # 'mention_everyone', 'mention_roles', 'mentions', 'nonce', 'pinned', 'referenced_message', 'sticker_items', timestamp', 'tts', 'type'

        # we do not want the bot to reply to itself
        if int(message.author['id']) == self.user.id or message.author.get('bot', False):
            return

        # Someone sent a DM to the bot.
        if not hasattr(message, 'guild_id'):
            await self.pitbot_module.handle_dm_commands(message)
            return

        # Check for pings
        if len(message.mentions) > 0 and int(message.mentions[0]['id']) == self.user.id:
            # Someone pinged the bot.
            await self.pitbot_module.handle_ping_commands(message)
            return

        # Someone used a command.
        if message.content.startswith(self.guild_config[message.guild_id]['command_character']):
            await self.pitbot_module.handle_commands(message)
            await self.sticker_module.handle_commands(message)
            await self.roulette_module.handle_commands(message)
            return

        # Check for stickers
        if hasattr(message, 'sticker_items'):
            self.sticker_module.update_sticker(message=message)

        # If none of the above was checked, its a regular message.
        # If message is empty it means someone just sent an attachment so ignore
        if message.content == '':
            return

        # We pass the message through our banword filter for automatic timeouts.
        await self.banword_module.handle_message(message)

    # Main 2 events to detect people joining and leaving.
    # These require Intents.Member to be enabled.
    async def on_guild_member_add(self, context: discord.Context) -> None:
        # 'avatar', 'communication_disabled_until', 'deaf', 'event_name', 'guild_id', 'is_pending', 'joined_at', 'mute', 'nick', 'pending', 'premium_since', 'roles', 'use
        # {'user': {'username': 'ConciseGrain063', 'public_flags': 0, 'id': '347958174864900096', 'discriminator': '0981', 'avatar': 'd9b2645a5cd4df04bf449d6739bbe182'}, 
        # 'roles': [], 'premium_since': None, 'pending': False, 'nick': None, 'mute': False, 'joined_at': '2021-11-13T15:42:00.448307+00:00', 'is_pending': False, 
        # 'guild_id': '553454168631934977', 'deaf': False, 'communication_disabled_until': None, 'avatar': None, 'event_name': 'GUILD_MEMBER_ADD'}
        user = context.user

        # Get timeout info
        timeout = self.pitbot_module.get_user_timeout(user)

        if timeout:
            # Add a strike to this user.
            strike_info = self.pitbot_module.add_strike(user=user, guild_id=context.guild_id,
                issuer_id=self.user.id, reason="User rejoined server after leaving during timeout.")

            if self.guild_config[context.guild_id]['log_channel']:
                await self.send_embed_message(self.guild_config[context.guild_id]['log_channel'], "User Rejoined after Timeout",
                    f"User: <@{user['id']}> was timed out, left the server and joined back again.")

            if self.guild_config[context.guild_id]['auto_timeout_on_reenter'] == True:
                for role in self.guild_config[context.guild_id]['ban_roles']:
                    await self.http.add_member_role(context.guild_id, user['id'], role, "User rejoined server after leaving during timeout.")

    async def on_guild_member_remove(self, context: discord.Context) -> None:
        # {'user': {'username': 'ConciseGrain063', 'public_flags': 0, 'id': '347958174864900096', 'discriminator': '0981', 
        # 'avatar': 'd9b2645a5cd4df04bf449d6739bbe182'}, 'guild_id': '553454168631934977'}}

        user = context.user

        # Get timeout info
        timeout = self.pitbot_module.get_user_timeout(user)

        if timeout:
            if self.guild_config[context.guild_id]['log_channel']:
                await self.send_embed_message(self.guild_config[context.guild_id]['log_channel'], "Timeout user left server",
                    f"User: <@{user['id']}> was timed out and left the server.")

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

    async def update_guild_configuration(self, guild):
        guild_config = self.db.load_server_configuration(guild, self)
        self.guild_config[guild.id] = guild_config