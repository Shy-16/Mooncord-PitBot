# -*- coding: utf-8 -*-

## Bot Module ##
# This is the main Bot module with functionality #

import logging
import traceback
import random
import time
from typing import Optional, Union

import discord
from database import Database
from log_utils import init_log
from modules import PitBot, Banwords, StickerStats, Roulette, Fluff, BattleRoyale
from application_commands import (
    set_help_slash,
    set_selfpit_slash,
    set_timeout_slash,
    set_timeoutns_slash,
    set_release_slash
)

log: logging.Logger = logging.getLogger("discord")


class Bot(discord.Bot):

    def __init__(self, config: dict) -> None:
        intents = discord.Intents.all()
        super().__init__(intents=intents)

        self.config = config
        self.guild_config = {}
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

    ## On error handler
    async def on_error(self, *args, **kwargs):
        exc_err = traceback.format_exc()
        log.error("Bot handled an error on event: {} with error:\r\n{}".format(args, exc_err))

    ### Client Events
    async def on_ready(self) -> None:
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
        
        # Setup help commands
        set_help_slash(self)
        set_selfpit_slash(self)

        # Setup role-based commands
        set_timeout_slash(self)
        set_timeoutns_slash(self)
        set_release_slash(self)

        # Init all tasks
        self.pitbot_module.init_tasks()
        self.banword_module.init_tasks()
        self.roulette_module.init_tasks()
        self.br_module.init_tasks()

        #activity = discord.Game("DM help for more info.")
        #await super().change_presence(activity=activity)

    async def on_message(self, message: discord.Message) -> None:
        """Handle create message event"""
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id or message.author.bot:
            return

        # Someone sent a DM to the bot.
        if not hasattr(message, 'guild'):
            await self.pitbot_module.handle_dm_commands(message)
            return

        # Check for pings
        if len(message.mentions) > 0 and message.mentions[0].id == self.user.id:
            # Someone pinged the bot.
            await self.pitbot_module.handle_ping_commands(message)
            await self.fluff_module.handle_ping_commands(message)
            return

        # Someone used a command.
        if message.content.startswith(self.guild_config[message.guild.id]['command_character']):
            await self.pitbot_module.handle_commands(message)
            await self.sticker_module.handle_commands(message)
            await self.roulette_module.handle_commands(message)
            await self.br_module.handle_commands(message)
            return

        # Check for stickers
        if message.stickers:
            self.sticker_module.update_sticker(message=message)

        # If none of the above was checked, its a regular message.
        # If message is empty it means someone just sent an attachment so ignore
        if message.content == '':
            return

        # We pass the message through our banword filter for automatic timeouts.
        await self.banword_module.handle_message(message)

    # Main 2 events to detect people joining and leaving.
    # These require Intents.Member to be enabled.
    async def on_guild_member_add(self, context: str) -> None:
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

    async def on_guild_member_remove(self, context: str) -> None:
        user = context.user

        # Get timeout info
        timeout = self.pitbot_module.get_user_timeout(user)

        if timeout:
            if self.guild_config[context.guild_id]['log_channel']:
                await self.send_embed_message(self.guild_config[context.guild_id]['log_channel'], "Timeout user left server",
                    f"User: <@{user['id']}> was timed out and left the server.")

    # Event to detect changes on roles
    # This also requires Intents.Member
    async def on_guild_member_update(self, context: str) -> None:
        '''Check if a member was updated.'''
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
                    except Exception:
                        # probably ran out of permissions, just skip
                        pass

                # delete roles from database
                self.db.delete_stored_roles(context.user['id'], context.guild_id)

    ### Utils
    def get_timeout_image(self):
        """Dont ask"""
        index = random.randint(0, len(self.default_guild['timeout_images']) -1)
        return self.default_guild['timeout_images'][index]

    async def send_message(self, channel: Union[int, discord.TextChannel], content: str="") -> dict:
        """Send a regular message on a channel"""
        try:
            if isinstance(channel, int):
                message = await self.get_channel(channel).send(content=content)
            else:
                message = await channel.send(content=content)
        except Exception:
            message = {}
        return message

    async def send_embed_message(self, channel: Union[int, discord.TextChannel], title: str="", description: str="", 
        color: int=0x0aeb06, fields: list=None, footer: dict=None, image: dict= None, view: Optional[discord.ui.View]=None) -> dict:
        """Sends an embed message to given channel_id"""
        embed = {
            "type": "rich",
            "title": title,
            "description": description,
            "color": color,
            "fields": fields or []
        }

        if footer is not None:
            embed['footer'] = footer

        if image is not None:
            embed['image'] = image

        try:
            if isinstance(channel, int):
                message = await self.get_channel(channel).send(embed=discord.Embed.from_dict(embed), view=view)
            else:
                message = await channel.send(embed=discord.Embed.from_dict(embed), view=view)
        except Exception:
            message = {}

        return message

    async def send_dm(self, user: Union[int, discord.User], content: str="") -> dict:
        """Send a regular DM"""
        try:
            if isinstance(user, int):
                dm_channel = await self.get_user(user).create_dm()
            else:
                dm_channel = await user.create_dm()
            message = await dm_channel.send(content=content)
        except Exception:
            message = {}
        return message

    async def send_embed_dm(self, user: Union[int, discord.User], title: str="", description: str="", color: int=0x0aeb06, fields: list=None,
        footer: dict=None, image: dict=None) -> dict:
        """Sends an embed DM to given user_id"""

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
            if isinstance(user, int):
                dm_channel = await self.get_user(user).create_dm()
            else:
                dm_channel = await user.create_dm()
            message = await dm_channel.send(embed=discord.Embed.from_dict(embed))
        except Exception:
            message = {}

        return message

    ### Helpers:
    def is_silent(self, guild_id) -> bool:
        """Return if silent including config and overrides."""
        if not self.config['discord']['silent'] and not self.guild_config[guild_id]['override_silent']:
                return False
        return True

    async def update_guild_configuration(self, guild):
        """Reload guild config after updating database"""
        guild_config = await self.db.load_server_configuration(guild, self)
        self.guild_config[guild.id] = guild_config
