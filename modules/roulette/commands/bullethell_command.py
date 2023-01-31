# -*- coding: utf-8 -*-

## BulletHell Command ##
# A command to randomly timeout someone. #

import asyncio
import random

from utils import MOD_LIST
from modules.context import CommandContext
from modules.command import Command
from log_utils import do_log


class BulletHellCommand(Command):
    """!bullethell / !bh"""
    async def execute(self, context: CommandContext) -> None:
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'bullethell'}, context=context)

        # Check cache and add to cache
        times = self._module.user_in_cache(str(context.author.id))
        self._module.add_user_to_cache(str(context.author.id))

        if times:
            # Let the user know in the channel about the cooldown
            info_message = f'You may use Roulette command only once a day. \r\n\
                Next reset cooldown is at <t:{self._module.get_reset_time()}:f> or <t:{self._module.get_reset_time()}:R>'
            await self._bot.send_embed_dm(context.author, 'Bullet Hell Info', info_message)
            try:
                await context.message.delete(reason='Command was on Cooldown')
            except Exception:
                # We can just ignore it, who cares.
                pass
            return

        # vars
        prefix = ["GIGA", "Weak", "Cum", "Burning", "Stinky", "Auto-aim", "Tracking"
                    "Weeb", "Penetrating", "Thrusting", "Slimy", "Invisible", "Holy",
                    "Daunting", "Demonic", "Bald", "Rimjob", "Femboy turning", "Catgirl turning",
                    "Ass gaping", "Mediocre", "Explosive", "Extra large", "Cheating"]
        suffix = ["OFHELL", "of Cum", "of Thrusting", "of Poop", "of Slime", "of Pride",
                    "of Rimjob", "of Goatsie", "of Balding", "up their ass", "of the Pit",
                    "of Fire and Destruction", "of the Abyss", "of the Unending Suffering",
                    "of the Deceased Souls", "of Happiness", "of Infinite Darkness",
                    "of Mediocrity", "Two Wives"]
        platinum = {'odds': 8, 'timeout': 43200} # 12h
        diamond = {'odds': 16, 'timeout': 57600} # 16h
        obsidian = {'odds': 24, 'timeout': 86400} # 24h
        cosmic = {'odds': 32, 'timeout': 129600} # 36h
        shiny = {'odds': 192, 'timeout': 172800} # 48h

        bullets = [shiny, cosmic, obsidian, diamond, platinum]
        for bullet in bullets:
            acc = random.randint(1, bullet['odds'])

            if acc == bullet['odds']:
                # Player got shot
                mod = random.choice(MOD_LIST)
                timeout = int(bullet['timeout']/3600)
                pre = random.choice(prefix)
                suff = random.choice(suffix)

                # Send a smug notification on the channel
                description = f"<@{context.author.id}> was hit by <@{mod}>'s {pre} bullet {suff}. " + \
                                f"BACK TO THE PIT for {timeout} hours."

                await self._bot.send_embed_message(context.channel, "Bullet Hell Winner", description)

                await asyncio.sleep(10)

                # Default reason
                reason = 'Automatic timeout issued for losing the bullet hell'

                # Issue the timeout
                self._bot.pitbot_module.add_timeout(user=context.author, guild_id=context.guild.id,
                    time=bullet['timeout'], issuer_id=self._bot.user.id, reason=reason, source='roulette')

                # Add the roles
                await context.author.add_roles(*context.ban_roles, reason=reason)

                # Send a DM to the user
                info_message = f"You've been pitted by {context.guild.name} mod staff for {timeout}h for losing the Bullet Hell. \r\n\
                    This timeout doesn't add any strikes to your acount.\r\n\r\n... loser."

                await self._bot.send_embed_dm(context.author, "Bullet Hell Winner", info_message)
                return

        # Delete invocation
        description = f"Mods missed every bullet. <@{context.author.id}>'s misery is unending."
        await self._bot.send_embed_message(context.channel, "Bullet Hell Loser", description)

    async def send_help(self, context: CommandContext) -> None:
        """
        Sends Help information to the channel
        """

        fields = [
            {'name': 'Help', 'value': f"Use {context.command_character}bullethell or {context.command_character}bh to win or lose.", 'inline': False},
        ]

        await self._bot.send_embed_message(context.channel, "Bullet Hell Info", fields=fields)
