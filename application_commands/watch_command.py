# -*- coding: utf-8 -*-

import discord
from discord import option, default_permissions


def watch(bot: discord.Client) -> None:
    @bot.slash_command(
        name="watch",
        description="Add a user to watchlist.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(moderate_members=True)
    @option("user", discord.User, description="User to be added.", required=True)
    @option("reason", str, description="Optional: Reason for adding.", required=False)
    async def handle_watch_slash(
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        if not reason or reason is None:
            reason ="No reason specified."
        
        log_channel = int(bot.guild_config[ctx.guild.id]['log_channel'])
        bot.watchlist_module.create_watchlist_entry(user=user, guild_id=ctx.guild.id,
            issuer_id=ctx.author.id, reason=reason)

        # Answer the request
        embed = {
            "type": "rich",
            "title": "/watch",
            "description": f"<@{user.id}> was added to watchlist.",
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)

        # Post information in 
        if not bot.silent and log_channel:
            info_message = f"<@{user.id}> was added to watchlist."
            await bot.send_embed_message(log_channel, "Watch User", info_message)


def unwatch(bot: discord.Client) -> None:
    @bot.slash_command(
        name="unwatch",
        description="Remove a user from watchlist.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(moderate_members=True)
    @option("user", discord.User, description="User to be added.", required=True)
    async def handle_unwatch_slash(
        ctx: discord.ApplicationContext,
        user: discord.User
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        
        log_channel = int(bot.guild_config[ctx.guild.id]['log_channel'])
        bot.watchlist_module.delete_watchlist_entry(user=user)

        # Answer the request
        embed = {
            "type": "rich",
            "title": "/unwatch",
            "description": f"<@{user.id}> was added to watchlist.",
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)

        # Post information in 
        if not bot.silent and log_channel:
            info_message = f"<@{user.id}> was removed from watchlist."
            await bot.send_embed_message(log_channel, "UnWatch User", info_message)

def watchlist(bot: discord.Client) -> None:
    @bot.slash_command(
        name="watchlist",
        description="Show watchlist.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(moderate_members=True)
    async def handle_watchlist_slash(
        ctx: discord.ApplicationContext
    ) -> None:
        await ctx.response.defer(ephemeral=True)

        entries = bot.watchlist_module.get_watchlist(status="active")
        userlist = "\r\n".join([f"<@{entry['user_id']}> ({entry['user_id']})\r\n{entry['reason'] or '*No reason given*'}\r\n" 
                                    for entry in entries[:30]])
        if not userlist or len(userlist) == 0:
            userlist = "*There are no users in the watchlist*"

        # Answer the request
        embed = {
            "type": "rich",
            "title": "/watchlist",
            "description": userlist,
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)
