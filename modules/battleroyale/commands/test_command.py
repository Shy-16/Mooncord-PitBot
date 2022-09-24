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

        test_users = [
            {'id': '137736942249967617',
                'username': 'Ryukin', 'discriminator': '7818'},
            {'id': '464457561584828416',
                'username': 'EN3MIES', 'discriminator': '0111'},
            {'id': '137736942249967617',
                'username': 'HexaSwell', 'discriminator': '0001'},
            {'id': '137254817943912448',
                'username': 'SLiK', 'discriminator': '2239'},
            {'id': '90260276431065088',
                'username': 'Mira', 'discriminator': '9287'},
            {'id': '665731528801779722',
                'username': 'BronzeBrowser', 'discriminator': '1420'},
            {'id': '340451087397945344',
                'username': 'Wolrosh', 'discriminator': '8739'},
            {'id': '244256653350928394',
                'username': 'adman731', 'discriminator': '9221'},
            {'id': '198461501894295552',
                'username': 'CyanideCocoa', 'discriminator': '8380'},
            {'id': '233351152119447553',
                'username': 'Chilly', 'discriminator': '4031'},
            {'id': '165289791708069888',
                'username': 'Yagi', 'discriminator': '7506'},
            {'id': '394532872117288963',
                'username': 'Shekel', 'discriminator': '3620'},
            {'id': '130976019321585664',
                'username': 'Eufra', 'discriminator': '7864'},
            {'id': '228073340441591808',
                'username': 'Menke', 'discriminator': '8099'},
            {'id': '147965531746467840',
                'username': 'Yeetloaf', 'discriminator': '3939'},
            {'id': '97450304018083840',
                'username': 'VerbalSilence', 'discriminator': '2171'}
        ]


        user_template = {'user': {
                            'username': 'yuigahamayui', 'public_flags': 128,
                            'id': '539881999926689829', 'discriminator': '7441',
                            'avatar': '31f61997206954399620accc101c5928'
                        },
                        'roles': [], 'premium_since': None,
                        'permissions': '4398046511103',
                        'pending': False, 'nick': 'whocares', 'mute': False,
                        'joined_at': '2019-03-08T05:49:16.519000+00:00',
                        'is_pending': False, 'deaf': False,
                        'communication_disabled_until': None, 'avatar': None}

        # check if there is a number as parameter
        for user in test_users:
            user_template['user']['id'] = user['id']
            user_template['user']['username'] = user['username']
            user_template['user']['discriminator'] = user['discriminator']
            self._module.game.add_participant(user_template)

        await self._module._bot.send_embed_message(self._module.game._setup_message['channel_id'], f"Added test participants")
        self._module.game._edit_cd = True
