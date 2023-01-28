# -*- coding: utf-8 -*-

## BR button Component ##
# A button to allow people to join BR. #

import discord


def help_select_dropdown(bot: discord.Bot, disabled: bool=False):
    bot_modules = [discord.SelectOption(label=opt.capitalize(), value=opt)
                    for opt in bot.all_modules.keys()]
    class HelpSelect(discord.ui.View):
        @discord.ui.select(
            placeholder="Select a module",
            custom_id="help_select_module",
            min_values=1,
            max_values=1,
            options=bot_modules,
            disabled=disabled)
        async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            embed = bot.all_modules[select.values[0]].get_help(interaction)

            await interaction.edit_original_response(embed=discord.Embed.from_dict(embed), view=self)

    return HelpSelect()
