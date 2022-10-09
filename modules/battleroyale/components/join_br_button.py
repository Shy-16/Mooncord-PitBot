# -*- coding: utf-8 -*-

## BR button Component ##
# A button to allow people to join BR. #

import discord


def create_br_button(bot: discord.Bot, disabled: bool=False):
    class JoinBRButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Join BR",
            custom_id="join_br_button",
            style=discord.ButtonStyle.secondary,
            emoji="👑",
            disabled=disabled)
        async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            br_module = bot.br_module

            # First of all verify there are enough spots
            if len(br_module.game.participants) >= br_module.game.max_participants:
                embed = {
                    "type": "rich",
                    "title": "BR Full",
                    "description": "Sorry better luck next time.",
                    "color": 0x0aeb06
                }
                await interaction.followup.send(embed=discord.Embed.from_dict(embed), ephemeral=True)
                button.disabled = True
                await interaction.response.edit_message(view=self)

            # second, verify the user is not in the tournament already
            if br_module.game.has_participant(interaction.user):
                embed = {
                    "type": "rich",
                    "title": "BR Status",
                    "description": "You are already signed up for this BR.",
                    "color": 0x0aeb06
                }
                await interaction.followup.send(embed=discord.Embed.from_dict(embed), ephemeral=True)
                return

            # third, add this user to the BR
            br_module.game.add_participant(interaction.user)

            embed = {
                "type": "rich",
                "title": "BR Joined",
                "description": "Get the juice ready, you've joined this BR.",
                "color": 0x0aeb06
            }
            await interaction.followup.send(embed=discord.Embed.from_dict(embed), ephemeral=True)

            # finally update the message to reflect the new added member
            br_module.game._edit_cd = True

    return JoinBRButton()
