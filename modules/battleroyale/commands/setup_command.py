# -*- coding: utf-8 -*-

## SetupBRCommand Command ##
# A command to setup BR event. #

from modules.context import CommandContext
from modules.command import Command, verify_permission
from modules.battleroyale.components import create_br_button


class SetupBRCommand(Command):
    """
    !setup_br
    """

    def __init__(self, br, permission: str = 'mod', dm_keywords: list = None) -> None:
        super().__init__(br, permission, dm_keywords)

    @verify_permission
    async def execute(self, context: CommandContext) -> None:

        # check if there is a number as parameter
        max_participants = self._module.DEFAULT_MAX_PARTICIPANTS
        if len(context.params) > 0 and context.params[0].isnumeric():
            max_participants = context.params[0]

        # create a new game
        await self._module.create_game(max_participants)

        # First send rules message
        content = f'''
        **Mooncord Battle Royale**

        {self._module.game.max_participants} players will compete, \
        {self._module.game.max_participants-1} will get pitted and only 1 will claim the #1 Victory Royale.

        Rules are as follow:
        - Click the 👑 to join. Once you join you can't leave.
        - The amount of time you get pitted for increases depending on how long you survive.
        -- Early rounds will get 1h and it will gradually increase up to 24h.
        -- Pit is handled through discord Timeout feature and not PitBot pit.
        - All the events and the people participating in them are **random**.

        If you win the #1 Victory Royale you get to live, a cool role for a week or two and to brag about it until nobody cares anymore.
        '''

        await self._bot.send_embed_message(context.channel, "Battle Royale", content)

        # Then create the join message
        content = f"To join Battle Royale react with 👑\r\n\r\n\
        There are currently {len(self._module.game.participants)} / {self._module.game.max_participants} ready to battle."
        footer = {
            "text": f"{self._bot.guild_config[context.guild.id]['name']} · Made by Yui"
        }

        # Setup the button
        button = create_br_button(self._bot)
        setup_message: dict = \
            await self._bot.send_embed_message(context.channel_id, "Battle Royale", content, color=10038562, footer=footer, view=button)
        self._module.game._setup_message = setup_message
        await self._module.start_game_director()
