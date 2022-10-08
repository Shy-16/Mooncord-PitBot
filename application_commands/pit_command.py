# -*- coding: utf-8 -*-

import discord
from discord.enums import OptionType

from .context import ApplicationCommandContext
from utils import iso_to_datetime, date_string_to_timedelta

def selfpit(bot: discord.Client):
	@bot.command(
		type=1,
		name="selfpit",
		description="Send yourself to the pit.",
		scope=int(bot.config['discord']['default_server_id']),
		options=[{"name":"time", "description":"<1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.",
			"required":True, "type":int(OptionType.STRING)}]
	)
	async def handle_selfpit_slash(ctx: str) -> None:
		# ctx: 'application_id', 'channel_id', 'data', 'guild_id', 'id', 'member', 'send', 'token', 'type', 'version'
		# ctx.member: {'username': 'yuigahamayui', 'public_flags': 128, 'id': '539881999926689829', 'discriminator': '7441', 
		#    'avatar': 'f493550c33cd55aaa0819be4e9a988a6', 'roles': ['553472623300968448', ...], 'premium_since': None, 'permissions': '1099511627775',
		#    'pending': False, 'nick': 'yui', 'mute': False, 'joined_at': '2019-03-08T05:49:16.519000+00:00', 'is_pending': False, 'deaf': False, 
		#    'communication_disabled_until': None, 'avatar': None}
		# ctx.data: {'type': 1, 'options': [{'value': '2d', 'type': 3, 'name': 'time'}], 'name': 'modmail', 'id': '905174418228125776'}

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

		user = context.member
		amount = context.options_dict['time']
		delta = date_string_to_timedelta(amount)

		if not delta:
			# Let the user know they fucked up.
			embed = {
				"type": "rich",
				"title": "Timeout error",
				"description": f"The time is not following the right format: {amount}.",
				"color": 0x0aeb06,
				"fields": [
					{
						'name': 'time',
						'value': 'The time parameter expects the following format: <1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.'
					}
				],
				"footer": {
					"text": f'{context.guild.name} Mod Team'
				}
			}

			data = {
				"tts": False,
				"content": "",
				"embeds": [embed],
				"allowed_mentions": { "parse": [] },
				"flags": 64
			}

			await bot.http.edit_interaction_response(data, context.token, context.application_id)
			return

		if delta.total_seconds() < 3600 or delta.total_seconds() > 259200:
			# Let the user know there is a limit
			embed = {
				"type": "rich",
				"title": "Timeout error",
				"description": f"Time can only be between 1h and 3d.",
				"color": 0x0aeb06,
				"fields": [],
				"footer": {
					"text": f'{context.guild.name} Mod Team'
				}
			}

			data = {
				"tts": False,
				"content": "",
				"embeds": [embed],
				"allowed_mentions": { "parse": [] },
				"flags": 64
			}

			await bot.http.edit_interaction_response(data, context.token, context.application_id)
			return

		timeout_info = bot.pitbot_module.add_timeout(user=user, guild_id=context.guild_id,
				time=int(delta.total_seconds()), issuer_id=bot.user.id, reason="User requested to be pitted.")

		for role in context.ban_roles:
			await bot.http.add_member_role(context.guild.id, user['id'], role, "Timeout issued by a mod.")

		# Send information message to the mods
		await bot.send_embed_message(context.log_channel, "User Timeout", f"<@{user['id']}> requested to be timed out for {amount}.")

		# Now send a DM to a user and answer the request
		embed = {
			"type": "rich",
			"title": "/selfpit",
			"description": f"<@{user['id']}> requested to be timed out for {amount}.",
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

		# Send a DM to the user
		info_message = f"You've requested to be pitted for {amount}."

		await bot.send_embed_dm(user['id'], "User Timeout", info_message)

def timeout(bot: discord.Client) -> None:

	options = [
		{
			"name":"user",
			"description":"User to be pitted.",
			"required":True,
			"type":int(OptionType.USER) #6
		},
		{
			"name":"time",
			"description":"<1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.",
			"required":True,
			"type":int(OptionType.STRING) #3
		},
		{
			"name":"reason",
			"description":"Optional: Rason for the pit.",
			"required":False,
			"type":int(OptionType.STRING) #3
		}
	]

	# Since last update modmail now doesnt allow doing this, instead set default_permissions
	# permissions = [{"id": role, "type": 1, "permission": True} for role in bot.default_guild['admin_roles']+bot.default_guild['mod_roles']]
	default_member_permissions = str(1 << 40) # MODERATE_MEMBERS

	@bot.command(
		type=1,
		name="timeout",
		description="Send a user to the pit.",
		scope=int(bot.config['discord']['default_server_id']),
		options=options,
		default_member_permissions=default_member_permissions
	)
	async def handle_timeout_slash(ctx: str) -> None:
		# ctx: 'application_id', 'channel_id', 'data', 'guild_id', 'id', 'member', 'send', 'token', 'type', 'version'

		context = ApplicationCommandContext(bot, ctx)

		# Defer the message so we dont fuck up the command
		data = {
			"type": 5,
			"data": {
                "tts": False,
                "content": "Sending a user to the pit, please wait...",
                "embeds": [],
                "allowed_mentions": { "parse": [] },
                "flags": 64
            }
		}
		await bot.http.create_interaction_response(token=context.token, application_id=context.id, data=data)

		user_id = context.options_dict['user']
		user = context.options_mention[user_id]
		issued_by = context.member
		amount = context.options_dict['time']
		reason = context.options_dict['reason'] if context.options_dict.get('reason') else 'Reason not specified'

		delta = date_string_to_timedelta(amount)

		if not delta:
			# Let the user know they fucked up.
			embed = {
				"type": "rich",
				"title": "Timeout error",
				"description": f"The time is not following the right format: {amount}.",
				"color": 0x0aeb06,
				"fields": [
					{
						'name': 'time',
						'value': 'The time parameter expects the following format: <1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.'
					}
				],
				"footer": {
					"text": f'{context.guild.name} Mod Team'
				}
			}

			data = {
				"tts": False,
				"content": "",
				"embeds": [embed],
				"allowed_mentions": { "parse": [] },
				"flags": 64
			}

			await bot.http.edit_interaction_response(data, context.token, context.application_id)
			return

		strike_info = bot.pitbot_module.add_strike(user=user, guild_id=context.guild.id,
					issuer_id=issued_by['id'], reason=reason)
		timeout_info = bot.pitbot_module.add_timeout(user=user, guild_id=context.guild_id,
				time=int(delta.total_seconds()), issuer_id=issued_by['id'], reason=reason)

		for role in context.ban_roles:
			await bot.http.add_member_role(context.guild.id, user['id'], role, "Timeout issued by a mod.")

		# Answer the request
		embed = {
			"type": "rich",
			"title": "/timeout",
			"description": f"<@{user['id']}> was timed out for {amount}.",
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
		user_strikes = bot.pitbot_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

		if not context.is_silent and context.log_channel:
			user_timeouts = bot.pitbot_module.get_user_timeouts(user=user, status='expired')

			strike_text = ""
			if len(user_strikes) > 0:
				strike_messages = list()

				for strike in user_strikes[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
					strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{user['id']}> was timed out by <@{issued_by['id']}> for {amount}."

			fields = [
				{'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
				{'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
				{'name': '\u200B', 'value': strike_text, 'inline': False}
			]

			await bot.send_embed_message(context.log_channel, "User Timeout", info_message, fields=fields)

		# Send a DM to the user
		info_message = f"You've been pitted by {context.guild.name} mod staff for {amount} for the following reason:\n\n{reason}"

		fields = [
			{'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).\r\n"+
				f"If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
		]

		await bot.send_embed_dm(user['id'], "User Timeout", info_message, fields=fields)

def timeoutns(bot: discord.Client) -> None:

	options = [
		{
			"name":"user",
			"description":"User to be pitted.",
			"required":True,
			"type":int(OptionType.USER) #6
		},
		{
			"name":"time",
			"description":"<1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.",
			"required":True,
			"type":int(OptionType.STRING) #3
		},
		{
			"name":"reason",
			"description":"Optional: Rason for the pit.",
			"required":False,
			"type":int(OptionType.STRING) #3
		}
	]

	# Type 1 = ROLE, Type 2 = USER
	# permissions = [{"id": role, "type": 1, "permission": True} for role in bot.default_guild['admin_roles']+bot.default_guild['mod_roles']]
	default_member_permissions = str(1 << 40) # MODERATE_MEMBERS

	@bot.command(
		type=1,
		name="timeoutns",
		description="Send a user to the pit without a strike.",
		scope=int(bot.config['discord']['default_server_id']),
		options=options,
		default_member_permissions=default_member_permissions
	)
	async def handle_timeout_slash(ctx: str) -> None:
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
		amount = context.options_dict['time']
		reason = context.options_dict['reason'] if context.options_dict.get('reason') else 'Reason not specified'

		delta = date_string_to_timedelta(amount)

		if not delta:
			# Let the user know they fucked up.
			embed = {
				"type": "rich",
				"title": "Timeout error",
				"description": f"The time is not following the right format: {amount}.",
				"color": 0x0aeb06,
				"fields": [
					{
						'name': 'time',
						'value': 'The time parameter expects the following format: <1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.'
					}
				],
				"footer": {
					"text": f'{context.guild.name} Mod Team'
				}
			}

			data = {
				"tts": False,
				"content": "",
				"embeds": [embed],
				"allowed_mentions": { "parse": [] },
				"flags": 64
			}

			await bot.http.edit_interaction_response(data, context.token, context.application_id)
			return

		timeout_info = bot.pitbot_module.add_timeout(user=user, guild_id=context.guild_id,
				time=int(delta.total_seconds()), issuer_id=issued_by['id'], reason=reason)

		for role in context.ban_roles:
			await bot.http.add_member_role(context.guild.id, user['id'], role, "Timeout issued by a mod.")

		# Answer the request
		embed = {
			"type": "rich",
			"title": "/timeout",
			"description": f"<@{user['id']}> was timed out for {amount}.",
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
		user_strikes = bot.pitbot_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

		if not context.is_silent and context.log_channel:
			user_timeouts = bot.pitbot_module.get_user_timeouts(user=user, status='expired')

			strike_text = ""
			if len(user_strikes) > 0:
				strike_messages = list()

				for strike in user_strikes[:5]:
					date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
					issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
					strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

				strike_text = "```" + "\r\n".join(strike_messages) + "```"

			info_message = f"<@{user['id']}> was timed out by <@{issued_by['id']}> for {amount}."

			fields = [
				{'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
				{'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
				{'name': '\u200B', 'value': strike_text, 'inline': False}
			]

			await bot.send_embed_message(context.log_channel, "User Timeout", info_message, fields=fields)

		# Send a DM to the user
		info_message = f"You've been pitted by {context.guild.name} mod staff for {amount} for the following reason:\n\n{reason}"

		fields = [
			{'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).\r\n"+
				f"If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
			{'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
				to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
		]

		await bot.send_embed_dm(user['id'], "User Timeout", info_message, fields=fields)
