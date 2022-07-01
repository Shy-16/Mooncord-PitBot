# -*- coding: utf-8 -*-

## SetupBRCommand Command ##
# A command to setup BR event. #


from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log


class TestBRCommand(Command):
    """
    !test_br
    """

    def __init__(self, br, permission: str ='mod', dm_keywords: list = list()) -> None:
        super().__init__(br, permission, dm_keywords)

    @verify_permission
    async def execute(self, context: CommandContext) -> None:

        test_user = {'user': {
                        'username': 'yuigahamayui', 'public_flags': 128,
                        'id': '539881999926689829', 'discriminator': '7441',
                        'avatar': '31f61997206954399620accc101c5928'
                    },
                    'roles': [], 'premium_since': None,
                    'permissions': '4398046511103',
                    'pending': False, 'nick': 'yui', 'mute': False,
                    'joined_at': '2019-03-08T05:49:16.519000+00:00',
                    'is_pending': False, 'deaf': False,
                    'communication_disabled_until': None, 'avatar': None}

        # check if there is a number as parameter
        for i in range(32):
            self._module.game.add_participant(test_user)

        await self._module._bot.send_embed_message(self._module._setup_message['channel_id'], f"Added 32 participants")
