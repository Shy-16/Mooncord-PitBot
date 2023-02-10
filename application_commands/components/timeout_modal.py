# -*- coding: utf-8 -*-

## Timeout Modal ##
# The followup Modal to timeout users. #

from __future__ import annotations

import discord

from utils import iso_to_datetime, date_string_to_timedelta


class TimeoutModal(discord.ui.Modal):
    def __init__(self, *children, title: str, custom_id: str | None = None, 
                    timeout: float | None = None, bot: discord.Bot | None = None) -> None:
        super().__init__(*children, title=title, custom_id=custom_id, timeout=timeout)
        self._bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        pitbot_module = self._bot.pitbot_module
        strikes_module = self._bot.strikes_module
        
        log_channel = int(self._bot.guild_config[interaction.guild_id]['log_channel'])
        ban_roles = [discord.Object(int(role)) for role in self._bot.guild_config[interaction.guild_id]['ban_roles']]
        
        # {'custom_id': 'create_ticket_modal', 'components': [
        #     {'type': 1, 'components': [{'value': '559682864241967124', 'type': 4, 'custom_id': 'timeout_user_id'}]}, 
        #     {'type': 1, 'components': [{'value': '2g', 'type': 4, 'custom_id': 'timeout_time'}]}, 
        #     {'type': 1, 'components': [{'value': 'test', 'type': 4, 'custom_id': 'timeout_comment'}
        # ]}]}
        user_id = interaction.data['components'][0]['components'][0]['value']
        amount = interaction.data['components'][1]['components'][0]['value']
        reason = interaction.data['components'][2]['components'][0]['value']
        issuer = interaction.user

        user = await self._bot.get_guild(interaction.guild_id).fetch_member(int(user_id))
        delta = date_string_to_timedelta(amount)

        timeout_info = pitbot_module.get_user_timeout(user)
        extended = False

        if not timeout_info:
            timeout_info = pitbot_module.add_timeout(user=user, guild_id=interaction.guild_id,
                time=int(delta.total_seconds()), issuer_id=issuer.id, reason=reason)
        else:
            new_time = int(delta.total_seconds() + timeout_info['time'])
            timeout_info = pitbot_module.extend_timeout(user=user, time=new_time)
            extended = True

        await user.add_roles(*ban_roles, reason="Timeout issued by a mod.")
        user_strikes = strikes_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

        if log_channel:
            user_timeouts = pitbot_module.get_user_timeouts(user=user, status='expired')

            strike_text = "```No Previous Strikes```"
            if len(user_strikes) > 0:
                strike_messages = list()

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    strike_issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {strike_issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> was timed out by <@{issuer.id}> for {amount}."
            if extended:
                info_message = f"<@{user.id}>'s timeout has been extended by <@{issuer.id}> for {amount}."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]

            await self._bot.send_embed_message(log_channel, "User Timeout", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been pitted by {interaction.guild.name} mod staff for {amount} for the following reason:\n\n{reason}"
        if extended:
            info_message = f"Your active timeout in {interaction.guild.name} has been extended by {amount} for the following reason:\n\n{reason}"

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {interaction.guild.name} (including this one).\r\n"+
                "If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {interaction.guild.name}.", 'inline': False}
        ]

        await self._bot.send_embed_dm(user, "User Timeout", info_message, fields=fields)
