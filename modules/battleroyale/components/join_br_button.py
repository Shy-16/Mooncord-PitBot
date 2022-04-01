# -*- coding: utf-8 -*-

## BulletHell Command ##
# A command to randomly timeout someone. #

import asyncio
import discord
import random
import json
import pprint

def setup(bot: discord.Client):
	@bot.component(
		name="join_br_button"
	)
	async def handle_join_br_button(ctx: discord.InteractionContext):
		# ctx: 'application_id', 'channel_id', 'data', 'guild_id', 'id', 'member', 'send', 'token', 'type', 'version'
		#
		#
		# <Context version=1 type=3 token=<longtoken> message={'type': 0, 'tts': False, 'timestamp': '2022-03-28T00:43:46.577000+00:00', 
		# 'pinned': False, 'mentions': [], 'mention_roles': [], 'mention_everyone': False, 'id': '957802145443360828', 'flags': 0, 
		# 'embeds': [{'type': 'rich', 'title': 'Battle Royale', 'footer': {'text': "Yui's cuties · Made by Yui"}, 
		# 'description': "....", 'color': 10038562}], 'edited_timestamp': None, 'content': '', 
		# 'components': [{'type': 1, 'components': [{'type': 2, 'style': 2, 'label': 'Join BR', 'emoji': {'name': '👑'}, 'custom_id': 'join_br_button'}]}], 
		# 'channel_id': '593048383405555725', 'author': {'username': 'SayoBot', 'public_flags': 0, 'id': '559682864241967124', 'discriminator': '8468', 
		# 'bot': True, 'avatar': 'f9ca445262aceec05824336265b05ecc'}, 'attachments': []} 
		# member={'user': {'username': 'yuigahamayui', 'public_flags': 128, 'id': '539881999926689829', 'discriminator': '7441', 
		# 'avatar': '31f61997206954399620accc101c5928'}, 'roles': [...], 'premium_since': None, 'permissions': '4398046511103', 
		# 'pending': False, 'nick': 'yui', 'mute': False, 'joined_at': '2019-03-08T05:49:16.519000+00:00', 'is_pending': False, 'deaf': False, 
		# 'communication_disabled_until': None, 'avatar': None} locale=en-GB id=957802202183897098 guild_locale=en-US guild_id=553454168631934977 
		# data={'custom_id': 'join_br_button', 'component_type': 2} channel_id=593048383405555725 application_id=559682864241967124>

		# Defer the message so we dont fuck up the command
		data = {
			"type": 5,
			"data": {
                "tts": False,
                "content": "Checking if there is an available spot...",
                "embeds": [],
                "allowed_mentions": { "parse": [] },
                "flags": 64
            }
		}
		await bot.http.create_interaction_response(token=ctx.token, application_id=ctx.id, data=data)

		br_module = bot.br_module

		# First of all verify there are enough spots
		if len(br_module.participants) >= br_module._max_participants:
			# Reply its full
			embed = {
				"type": "rich",
				"title": "BR Full",
				"description": "Sorry better luck next time.",
				"color": 0x0aeb06
			}

			data = {
				"tts": False,
				"content": "",
				"embeds": [embed],
				"allowed_mentions": { "parse": [] },
				"flags": 64
			}

			await bot.http.edit_interaction_response(data, ctx.token, ctx.application_id)

			# then edit message to disable button
			button_component = {
				"type": 2, # button
				"style": 2, # secondary or gray
				"label": "Join BR",
				"emoji": {
					"id": None,
					"name": "👑",
					"animated": False
				},
				"custom_id": "join_br_button",
				"disabled": True
			}

			action_row = {
				"type": 1,
				"components": [button_component]
			}

			payload = {
				'components': [action_row]
			}

			await bot.http.edit_message(ctx.message['channel_id'], ctx.message['id'], payload)
			return

		# second, verify the user is not in the tournament already
		if ctx.member['user']['id'] in br_module.participants:
			# User is already in, so just reply saying they are in.
			embed = {
				"type": "rich",
				"title": "BR Status",
				"description": "You are already signed up for this BR.",
				"color": 0x0aeb06
			}

			data = {
				"tts": False,
				"content": "",
				"embeds": [embed],
				"allowed_mentions": { "parse": [] },
				"flags": 64
			}

			await bot.http.edit_interaction_response(data, ctx.token, ctx.application_id)
			return

		# third, add this user to the BR
		br_module.participants.append(ctx.member['user']['id'])

		embed = {
			"type": "rich",
			"title": "BR Joined",
			"description": "Get the juice ready, you've joined this BR.",
			"color": 0x0aeb06
		}

		data = {
			"tts": False,
			"content": "",
			"embeds": [embed],
			"allowed_mentions": { "parse": [] },
			"flags": 64
		}

		await bot.http.edit_interaction_response(data, ctx.token, ctx.application_id)

		# finally update the message to reflect the new added member
		br_module._edit_cd = True
