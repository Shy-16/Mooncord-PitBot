# -*- coding: utf-8 -*-

import discord
from discord import option, default_permissions


def colosseum(bot: discord.AutoShardedBot) -> None:
    cmd_group = bot.slash_group(
        name="Colosseum",
        description="Participate in the Colosseum.",
        guild_ids=[bot.guilds[0].id]
    )
    
    @bot.slash_command(
        name="duel",
        description="Send a duel request to .",
        parent=cmd_group
    )
    @default_permissions(send_messages=True)
    @option("user", discord.Member, description="User to duel.", required=True)
    @option("bet", int, description="Optional: Bet amount.", required=False)
    async def handle_colosseum_duel(
        ctx: discord.ApplicationContext,
        user: discord.Member,
        bet: int
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        
        col_module = bot.colosseum_module
        author = ctx.author
        
        # Check if there is already a duel opened from the other side
        col_module.get_duel(user, author)
