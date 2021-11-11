# -*- coding: utf-8 -*-

import discord

def setup(bot: discord.Client):
	@bot.command(
		type=1,
		name="help",
		description="Check PitBot help information.",
		scope=int(bot.config['discord']['default_server_id'])
	)
	async def handle_help_slash(ctx: discord.Context) -> None:
		# ctx: 'application_id', 'channel_id', 'data', 'guild_id', 'id', 'member', 'send', 'token', 'type', 'version'
		# ctx.member: {'username': 'yuigahamayui', 'public_flags': 128, 'id': '539881999926689829', 'discriminator': '7441', 
		#    'avatar': 'f493550c33cd55aaa0819be4e9a988a6', 'roles': ['553472623300968448', ...], 'premium_since': None, 'permissions': '1099511627775',
		#    'pending': False, 'nick': 'yui', 'mute': False, 'joined_at': '2019-03-08T05:49:16.519000+00:00', 'is_pending': False, 'deaf': False, 
		#    'communication_disabled_until': None, 'avatar': None}
		# ctx.data {'type': 1, 'name': 'help', 'id': '908378744807379035'}

		has_mod_permissions = False
		user = ctx.member

		if bot.is_ready():
			check_roles = bot.guild_config[ctx.guild_id]['admin_roles'] + bot.guild_config[ctx.guild_id]['mod_roles']
			has_mod_permissions = len([role for role in check_roles if user['roles'].count(role) > 0]) > 0

		if not has_mod_permissions:
			embed = {
				"type": "rich",
				"title": "PitBot Help",
				"description": f'This is the {bot.default_guild["name"]} moderation bot.',
				"color": 0x6658ff,
				"fields": [
					{
						'name': '/selfpit <time>',
						'value': f"/selfpit will send you to the pit for a certain time.\r\n"+ 
						"The time parameter expects the following format: <1-2 digit number><one of: s, m, h, d> where s is second, m is minute, h is hour, d is day.\r\n"+
						"Example: `/selfpit 2h` to be pitted for 2 hours.\r\n\r\n"+
						"**This is not a tool to play, if you use it you will stay pitted for the amount you set. There is no early releasing**"
					},
					{
					  "name": 'Additional Information',
					  "value": f'If you\'d like to review your disciplinary history in {bot.default_guild["name"]} DM me `strikes`.'
					}
				],
				"footer": {"text": f'{bot.default_guild["name"]} Mod Team'}
			}

		else:
			embed = {
				"type": "rich",
				"title": "PitBot Help",
				"description": "Executing the command with no arguments will always show the help for that command.",
				"color": 0x6658ff,
				"fields": [
					{'name': 'timeout', 'value': f"/timeout will set a timeout for a given user.\r\n"+ 
						f"The time parameter expects the following format: <1-2 digit number><one of: s, m, h, d> where s is second, m is minute, h is hour, d is day."},
					{'name': 'timeoutns', 'value': f"/imeoutns will set a timeout for a given user without adding a strike to their account."},
					{'name': 'release', 'value': f"/elease will end a user's timeout immediately.\r\n"+ 
						f"Optional parameter: `amend`: If amend is provided it will also delete the most recent strike issued to the user."},
					{'name': 'strikes', 'value': f"/strikes is used to add and remove strikes from a user or view a user's strike history."}
				],
				"footer": {"text": f'{bot.default_guild["name"]} Mod Team'}
			}

		data = {
			"type": 4,
			"data": {
                "tts": False,
                "content": "",
                "embeds": [embed],
                "allowed_mentions": { "parse": [] },
                "flags": 64
            }
		}
		await bot.http.create_interaction_response(token=ctx.token, application_id=ctx.id, data=data)
