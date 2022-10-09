# -*- coding: utf-8 -*-

## Start Command ##
# A command to start a BR event. #


from modules.context import CommandContext
from modules.command import Command, verify_permission


class StartBRCommand(Command):
    """
    !start_br
    """

    def __init__(self, br, permission: str = 'mod', dm_keywords: list = None) -> None:
        super().__init__(br, permission, dm_keywords)

    @verify_permission
    async def execute(self, context: CommandContext) -> None:

        # disable button so players can't join after it starts
        await self._module.disable_setup_button()

        content = '''
        **Mooncord Battle Royale**

        Starting now!
        '''
        await self._bot.send_embed_message(context.channel_id, "Battle Royale", content)
        self._module.game._started = True
