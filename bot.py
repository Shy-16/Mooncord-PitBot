# -*- coding: utf-8 -*-

## Bot Module ##
# This is the main Bot module with functionality #

import logging
import discord
import traceback
import random
import time
from typing import Optional

from database import Database
from log_utils import init_log, do_log
from modules import PitBot, Banwords, StickerStats, Roulette, BattleRoyale, Fluff
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
        self.br_module = BattleRoyale(bot=self)
        self.fluff_module = Fluff(bot=self)

        init_log()

        set_help_slash(self)
        set_selfpit_slash(self)

    def run(self, *, token: str) -> None:
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
            guild_config = await self.db.load_server_configuration(guild, self)
            self.guild_config[guild.id] = guild_config
            if self.default_guild is None: self.default_guild = guild_config
            log.info(f"Loaded configuration for guild: {guild.id}.")

        log.info('Finished loading all guild info.')
        log.info("All configuration finished.")

        # Setup role-based commands
        set_timeout_slash(self)
        set_timeoutns_slash(self)
        set_release_slash(self)

        # Init all tasks
        self.pitbot_module.init_tasks()
        self.banword_module.init_tasks()
        self.roulette_module.init_tasks()
        self.br_module.init_tasks()

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
            await self.fluff_module.handle_ping_commands(message)
            return

        # Someone used a command.
        if message.content.startswith(self.guild_config[message.guild_id]['command_character']):
            await self.pitbot_module.handle_commands(message)
            await self.sticker_module.handle_commands(message)
            await self.roulette_module.handle_commands(message)
            await self.br_module.handle_commands(message)
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
    async def on_guild_member_update(self, context: discord.Context) -> None:
        '''Check if a member was updated.'''

        #   {'user': {'username': 'MEE6', 'public_flags': 65536, 'id': '159985870458322944', 'discriminator': '4876', 'bot': True, 
        #           'avatar_decoration': None, 'avatar': 'b50adff099924dd5e6b72d13f77eb9d7'}, 
        #   'roles': ['553455586709078024', '561164821953904660', '553455365233311765'], 
        #   'premium_since': None, 'pending': False, 'nick': None, 'joined_at': '2019-03-08T05:54:01.336000+00:00', 'is_pending': False, 
        #   'guild_id': '553454168631934977', 'flags': 0, 'communication_disabled_until': None, 'avatar': None}}

        # This is related to resubbing and restoring permissions
        sub_roles = self.guild_config[context.guild_id]['sub_roles']
        resubbed = False

        for role in sub_roles:
            # If role is in context.roles they could've resubbed so quickly check.
            if role in context.roles:
                resubbed = True
                break

        if resubbed:
            user_roles = self.db.get_stored_roles(context.user['id'], context.guild_id)

            if user_roles:
                user_roles = dict(user_roles)

                for role in user_roles['roles']:
                    try:
                        await self.http.add_member_role(user_roles['guild_id'], user_roles['user_id'], role, "Role restored after resubbing.")
                        time.sleep(0.5) # stall hard to avoid ratelimiting, there is no rush to restore roles
                    except:
                        # probably ran out of permissions, just skip
                        pass

                # delete roles from database
                self.db.delete_stored_roles(context.user['id'], context.guild_id)

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
        try:
            message = await self.http.send_message(channel_id, content)
        except:
            message = dict()
        return message

    async def send_embed_message(self, channel_id: int, title: str = "", description: str = "", color: int = 0x0aeb06, fields: list = list(),
        footer: dict = None, image: dict= None, components: Optional[list] = None) -> dict:
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

        try:
            message = await self.http.send_message(channel_id, '', embed=embed, components=components)
        except:
            message = dict()

        return message

    async def send_dm(self, user_id: int, content: str = "") -> dict:
        try:
            dm_channel = await self.http.create_dm(user_id)
            message = await self.http.send_message(dm_channel['id'], content)
        except:
            message = dict()

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

        try:
            dm_channel = await self.http.create_dm(user_id)
            message = await self.http.send_message(dm_channel['id'], '', embed=embed)
        except:
            message = dict()

        return message

    ### Helpers:
    def is_silent(self, guild_id) -> bool:
        """Return if silent including config and overrides."""

        if not self.config['discord']['silent'] and not self.guild_config[guild_id]['override_silent']:
                return False

        return True

    async def update_guild_configuration(self, guild):
        guild_config = await self.db.load_server_configuration(guild, self)
        self.guild_config[guild.id] = guild_config