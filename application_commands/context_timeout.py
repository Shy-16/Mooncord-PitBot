# -*- coding: utf-8 -*-

import discord
from discord import default_permissions

from .components import TimeoutModal


def set_context_timeout(bot: discord.Bot):
    @bot.user_command(
        name="Timeout",
        guild_ids=[bot.guilds[0].id])
    @default_permissions(moderate_members=True)
    async def context_timeout(context: discord.ApplicationContext, user: discord.Member) -> None:
        user_id_input = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            custom_id="timeout_user_id",
            label="User ID",
            placeholder="Input the user Discord ID to timeout",
            min_length=8,
            max_length=64,
            required=True,
            value=user.id
        )
        time_input = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            custom_id="timeout_time",
            label="Time <1-2 digit number><one of: s, m, h, d>",
            placeholder="Ex: 30m, 2h, 12h, 36h, 3d",
            min_length=1,
            max_length=5,
            required=True
        )
        comment_input = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            custom_id="timeout_comment",
            label="Comment",
            placeholder="Ex: breaking TOS",
            required=False
        )
        modal = TimeoutModal(user_id_input, time_input, comment_input,
                            title="Timeout User", custom_id="timeout_modal", bot=bot)
        await context.response.send_modal(modal)
