# -*- coding: utf-8 -*-

## Test Command ##
# Adds a list of test users for the BR event. #


from modules.context import CommandContext
from modules.command import Command, verify_permission


class DummyMember:
    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        self.discriminator = data['discriminator']

class TestBRCommand(Command):
    """!test_br"""
    @verify_permission
    async def execute(self, context: CommandContext) -> None:

        test_users = [
            {'id': '137736942249967617',
                'name': 'Ryukin', 'discriminator': '7818'},
            {'id': '464457561584828416',
                'name': 'EN3MIES', 'discriminator': '0111'},
            {'id': '137736942249967617',
                'name': 'HexaSwell', 'discriminator': '0001'},
            {'id': '137254817943912448',
                'name': 'SLiK', 'discriminator': '2239'},
            {'id': '90260276431065088',
                'name': 'Mira', 'discriminator': '9287'},
            {'id': '665731528801779722',
                'name': 'BronzeBrowser', 'discriminator': '1420'},
            {'id': '340451087397945344',
                'name': 'Wolrosh', 'discriminator': '8739'},
            {'id': '244256653350928394',
                'name': 'adman731', 'discriminator': '9221'},
            {'id': '198461501894295552',
                'name': 'CyanideCocoa', 'discriminator': '8380'},
            {'id': '233351152119447553',
                'name': 'Chilly', 'discriminator': '4031'},
            {'id': '165289791708069888',
                'name': 'Yagi', 'discriminator': '7506'},
            {'id': '394532872117288963',
                'name': 'Shekel', 'discriminator': '3620'},
            {'id': '130976019321585664',
                'name': 'Eufra', 'discriminator': '7864'},
            {'id': '228073340441591808',
                'name': 'Menke', 'discriminator': '8099'},
            {'id': '147965531746467840',
                'name': 'Yeetloaf', 'discriminator': '3939'},
            {'id': '97450304018083840',
                'name': 'VerbalSilence', 'discriminator': '2171'},
            {'id': '186350500780834817',
                'name': 'Skurkitty', 'discriminator': '7052'},
            {'id': '1002375116077944882',
                'name': 'peacefulhaley', 'discriminator': '3738'},
            {'id': '153596415128502273',
                'name': 'thorgot', 'discriminator': '5851'},
            {'id': '977222975738744882',
                'name': 'Metal', 'discriminator': '9020'},
            {'id': '101880837301096448',
                'name': 'AbeX300', 'discriminator': '7213'},
            {'id': '121075890372214784',
                'name': 'PokeYourWaffle', 'discriminator': '0310'},
            {'id': '129659119358574592',
                'name': 'EnDecc', 'discriminator': '9038'},
            {'id': '437665928835104769',
                'name': 'Ravenaura', 'discriminator': '4480'},
        ]

        # check if there is a number as parameter
        for user in test_users:
            self._module.game.add_participant(DummyMember(user))

        await self._module._bot.send_embed_message(self._module.game._setup_message.channel, "Added test participants")
        self._module.game._edit_cd = True
