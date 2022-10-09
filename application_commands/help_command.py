# -*- coding: utf-8 -*-

import discord

def setup(bot: discord.Bot):
    @bot.slash_command(
        name="help",
        description="Check PitBot help information.",
        guild_ids=[bot.guilds[0].id]
    )
    async def handle_help_slash(ctx: discord.ApplicationContext) -> None:
        check_roles = bot.guild_config[ctx.guild_id]['admin_roles'] + bot.guild_config[ctx.guild_id]['mod_roles']
        has_mod_permissions = len([role for role in ctx.user.roles if str(role.id) in check_roles]) > 0

        if not has_mod_permissions:
            embed = {
                "type": "rich",
                "title": "PitBot Help",
                "description": f'This is the {ctx.guild.name} moderation bot.',
                "color": 0x6658ff,
                "fields": [
                    {
                        'name': '/selfpit <time>',
                        'value': "/selfpit will send you to the pit for a certain time.\r\n"+ 
                        "The time parameter expects the following format: <1-2 digit number><one of: s, m, h, d> where s is second, m is minute, h is hour, d is day.\r\n"+
                        "Example: `/selfpit 2h` to be pitted for 2 hours.\r\n\r\n"+
                        "**This is not a tool to play, if you use it you will stay pitted for the amount you set. There is no early releasing**"
                    },
                    {
                        "name": 'Additional Information',
                        "value": f'If you\'d like to review your disciplinary history in {ctx.guild.name} DM me `strikes`.'
                    }
                ],
                "footer": {"text": f'{ctx.guild.name} Mod Team'}
            }

        else:
            embed = {
                "type": "rich",
                "title": "PitBot Help",
                "description": "Executing the command with no arguments will always show the help for that command.",
                "color": 0x6658ff,
                "fields": [
                    {'name': 'timeout', 'value': "/timeout will set a timeout for a given user.\r\n"+ 
                        "The time parameter expects the following format: <1-2 digit number><one of: s, m, h, d> where s is second, m is minute, h is hour, d is day."},
                    {'name': 'timeoutns', 'value': "/imeoutns will set a timeout for a given user without adding a strike to their account."},
                    {'name': 'release', 'value': "/elease will end a user's timeout immediately.\r\n"+ 
                        "Optional parameter: `amend`: If amend is provided it will also delete the most recent strike issued to the user."},
                    {'name': 'strikes', 'value': "/strikes is used to add and remove strikes from a user or view a user's strike history."}
                ],
                "footer": {"text": f'{ctx.guild.name} Mod Team'}
            }

        await ctx.response.send_message(embed=discord.Embed.from_dict(embed), ephemeral=True)
