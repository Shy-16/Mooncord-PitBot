# -*- coding: utf-8 -*-

import discord
from discord.enums import OptionType

from .context import ApplicationCommandContext
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string

def release(bot: discord.Client) -> None:

	options = [
		{
			"name":"user",
			"description":"User to be released.",
			"required":True,
			"type":int(OptionType.USER) #6
		},
		{
			"name":"amend",
			"description":"Optional: Rason for the pit.",
			"required":False,
			"type":int(OptionType.BOOLEAN) #5
		}
	]

	# Type 1 = ROLE, Type 2 = USER
	permissions = [{"id": role, "type": 1, "permission": True} for role in bot.default_guild['admin_roles']+bot.default_guild['mod_roles']]

	@bot.command(
		type=1,
		name="release",
		description="Send a user to the pit without a strike.",
		scope=int(bot.config['discord']['default_server_id']),
		options=options,
		permissions=permissions
	)
	async def handle_timeout_slash(ctx: discord.Context) -> None:
		# ctx: 'application_id', 'channel_id', 'data', 'guild_id', 'id', 'member', 'send', 'token', 'type', 'version'

		context = ApplicationCommandContext(bot, ctx)

		# Defer the message so we dont fuck up the command
		data = {
			"type": 5,
			"data": {
                "tts": False,
                "content": "Pitting yourself, please wait...",
                "embeds": [],
                "allowed_mentions": { "parse": [] },
                "flags": 64
            }
		}
		await bot.http.create_interaction_response(token=context.token, application_id=context.id, data=data)

		user_id = context.options_dict['user']
		user = context.options_mention[user_id]
		issued_by = context.member
		amend = context.options_dict.get('amend')

		for role in context.ban_roles:
			await bot.http.remove_member_role(context.guild.id, user['id'], role, "User released by a mod.")

		timeout_info = bot.pitbot_module.expire_timeout(user=user)
		strike_info = None

		if amend:
			strike_info = bot.pitbot_module.delete_strike(user=user)

		# Answer the request
		embed = {
			"type": "rich",
			"title": "/timeout",
			"description": f"<@{user['id']}> was released from the pit.",
			"color": 0x6658ff,
			"fields": [],
			"footer": {"text": f'{bot.default_guild["name"]} Mod Team'}
		}

		data = {
			"tts": False,
			"content": "",
			"embeds": [embed],
			"allowed_mentions": { "parse": [] },
			"flags": 64
		}

		await bot.http.edit_interaction_response(data, ctx.token, ctx.application_id)

		# Post information in 
		if not context.is_silent and context.log_channel:
			user_strikes = bot.pitbot_module.get_user_strikes(user, sort=('_id', -1), partial=False)
			user_timeouts = bot.pitbot_module.get_user_timeouts(user=user, status='expired')

			strike_text = ""
			if len(user_strikes) > 0:
				strike_messages = list()

				for strike in user_strikes[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
					strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{user['id']}> wasn't timed out."
			if timeout_info:
				info_message = f"<@{user['id']}> was released by <@{issued_by['id']}>."

			if strike_info:
				info_message += f"\r\n\r\nUser's last strike was deleted."

			fields = [
				{'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
				{'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
				{'name': '\u200B', 'value': strike_text, 'inline': False}
			]

			await bot.send_embed_message(context.log_channel, "Release user", info_message, fields=fields)

		# Send a DM to the user
		info_message = f"You've been released from the pit by {context.guild.name} mod staff."
		if strike_info:
				info_message += f"\r\n\r\nYour last strike was additionally deleted."

		fields = [
			{'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
		]

		await bot.send_embed_dm(user['id'], "User Timeout", info_message, fields=fields)