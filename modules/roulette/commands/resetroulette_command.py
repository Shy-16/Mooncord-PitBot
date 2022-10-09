# -*- coding: utf-8 -*-

## RouletteCommand ##
# A command to randomly timeout someone. #

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log

class ResetRouletteCommand(Command):
    """
    !resetroulette @user|ID
    !rr @user|ID
    """

    def __init__(self, roulette, permission: str ='mod', dm_keywords: list = None) -> None:
        super().__init__(roulette, permission, dm_keywords)

    @verify_permission
    async def execute(self, context: CommandContext) -> None:

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'resetroulette'}, context=context)

        user_id = None

        # We either need a mention or an ID as first parameter.
        if not context.mentions:
            user_id = context.params[0]
            # review its a "valid" snowflake
            if not len(user_id) > 16:
                await self.send_help(context)
                return

            user = self._module.get_user(user_id=user_id)

            if not user:
                # there is a possibility user is not yet in our database
                user = await self._bot.get_user(user_id)

        else:
            user = context.mentions[0]
            
        if isinstance(user, int):
            user = self._bot.get_user(user)
        elif isinstance(user, dict):
            user = context.guild.get_member(int(user['discord_id']))

        # reset from cache
        self._module.remove_user_from_cache(str(user.id))

        # react to message
        await context.message.add_reaction("✅")

    async def send_help(self, context: CommandContext) -> None:
        """
        Sends Help information to the channel
        """

        fields = [
            {'name': 'Help', 'value': f"Use {context.command_character}rr @user|ID to reset their cache on BH.", 'inline': False},
        ]

        await self._bot.send_embed_message(context.channel.id, "Reset Roulette", fields=fields)
