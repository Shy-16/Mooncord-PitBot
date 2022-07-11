# -*- coding: utf-8 -*-

## BulletHell Command ##
# A command to randomly timeout someone. #

import asyncio
import random
import json

from modules.context import CommandContext
from modules.command import Command
from log_utils import do_log


class BulletHellCommand(Command):
    """
    !bullethell <type|optional|all>
    !bh
    !bh all
    !bh silver
    """

    def __init__(self, roulette, permission: str ='mod', dm_keywords: list = list()) -> None:
        super().__init__(roulette, permission, dm_keywords)

    async def execute(self, context: CommandContext) -> None:

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'bullethell'}, context=context)

        # Check cache and add to cache
        times = self._module.user_in_cache(context.author['id'])
        self._module.add_user_to_cache(context.author['id'])

        if times:
            # Let the user know in the channel about the cooldown
            info_message = f'You may use Roulette command only once a day. \r\n\
                Next reset cooldown is at <t:{self._module.get_reset_time()}:f> or <t:{self._module.get_reset_time()}:R>'
            await self._bot.send_embed_dm(context.author['id'], 'Bullet Hell Info', info_message)
            try:
                await self._bot.http.delete_message(context.channel_id, context.id, 'Command was on Cooldown')
            except:
                # We can just ignore it, who cares.
                pass
            return

        # vars
        lead = {'name': 'Lead', 'odds': 2, 'timeout': 7200} # 2h
        silver = {'name': 'Silver', 'odds': 3, 'timeout': 14400} # 4h
        gold = {'name': 'Gold', 'odds': 4, 'timeout': 28800} # 8h
        platinum = {'name': 'Platinum', 'odds': 6, 'timeout': 43200} # 12h
        diamond = {'name': 'Diamond', 'odds': 8, 'timeout': 57600} # 16h
        obsidian = {'name': 'Obsidian', 'odds': 10, 'timeout': 86400} # 24h
        cosmic = {'name': 'Cosmic', 'odds': 12, 'timeout': 129600} # 36h
        shiny = {'name': 'Shiny', 'odds': 4096, 'timeout': 172800} # 48h

        bullets = [shiny, cosmic, obsidian, diamond, platinum, gold, silver, lead]
        mods = [
            '468937023307120660', # Moon
            '186562579412418560', # Amaya
            '178015162287128576', # Brock
            '157411268624384002', # Cheeky
            '177904844412026880', # Duke
             '69945889182986240', # Grimace
            '117373803344035841', # Jestar
            '187308638321246209', # Kyro
             '66292645407760384', # IpN
            '115843971804037120', # Nyx
            '184528528572678145', # Shy
            '109782272663629824', # Sunshine
            '539881999926689829', # Yui
        ]

        for bullet in bullets:
            acc = random.randint(1, bullet['odds'])

            if acc == bullet['odds']:
                # Player got shot
                mod = mods[random.randint(0, len(mods)-1)]
                timeout = int(bullet['timeout']/3600)

                # Send a smug notification on the channel
                description = f"<@{context.author['id']}> stands tall in front of the Stormtrooper Mod team, ready to face their destiny.\r\n \
                    **BANG!** A {bullet['name']} bullet shot by <@{mod}> went straight through <@{context.author['id']}>'s skull.\r\n\
                    BACK TO THE PIT for {timeout} hour{'s' if timeout > 1 else ''}"

                await self._bot.send_embed_message(context.channel_id, "Bullet Hell Loser", description)

                await asyncio.sleep(10)

                # Default reason
                reason = 'Automatic timeout issued for losing the bullet hell'

                # Issue the timeout
                timeout_info = self._bot.pitbot_module.add_timeout(user=context.author, guild_id=context.guild.id,
                    time=bullet['timeout'], issuer_id=self._bot.user.id, reason=reason, source='roulette')

                # Add the roles
                for role in context.ban_roles:
                    await self._bot.http.add_member_role(context.guild.id, context.author['id'], role, reason)

                # generate logs in proper channel
                if context.log_channel:
                    self._module._timeouts.append(f"<@{context.author['id']}> bh {timeout}h")

                # Send a DM to the user
                info_message = f"You've been pitted by {context.guild.name} mod staff for {timeout}h for losing the Bullet Hell. \r\n\
                    This timeout doesn't add any strikes to your acount.\r\n\r\n... loser."

                await self._bot.send_embed_dm(context.author['id'], "Bullet Hell Loser", info_message)
                return

        # Send a notification on the channel
        description = f"<@{context.author['id']}> stands tall in front of the Stormtrooper Mod team, ready to face their destiny.\r\n \
                    *thud* *thunk* All the bullets miss the mark hitting the wall behind <@{context.author['id']}>\r\n"

        await self._bot.send_embed_message(context.channel_id, "Bullet Hell Winner", description)

    async def send_help(self, context: CommandContext) -> None:
        """
        Sends Help information to the channel
        """

        fields = [
            {'name': 'Help', 'value': f"Use {context.command_character}bullethell or {context.command_character}bh to win or lose.", 'inline': False},
        ]

        await self._bot.send_embed_message(context.channel_id, "Bullet Hell Info", fields=fields)
