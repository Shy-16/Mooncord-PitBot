# -*- coding: utf-8 -*-

## Roulette Module ##
# Fluff roulette minigame where people gamble a pit #

import logging
import datetime
from typing import Any

import discord

from utils import MOD_LIST
from modules.command import Command
from modules.context import CommandContext, InteractionContext
from modules.battleroyale.components import create_br_button
from .commands import SetupBRCommand, StartBRCommand, TestBRCommand
from .br_game import BRGame

log: logging.Logger = logging.getLogger("br")


class BattleRoyale:
    DEFAULT_MAX_PARTICIPANTS = 128

    def __init__(self, *, bot: discord.Bot) -> None:
        self._bot: discord.Bot = bot

        self._game: BRGame = None

        self.commands: dict[str, Command] = {
            "setup_br": SetupBRCommand(self, 'mod'),
            "start_br": StartBRCommand(self, 'mod'),
            "test_br": TestBRCommand(self, 'mod')
        }

    @property
    def game(self):
        return self._game

    def init_tasks(self) -> None:
        """Initialize the different tasks that run in the background"""

    async def handle_commands(self, message: str) -> None:
        """Handles any commands given through the designed character"""

        command = message.content.replace(self._bot.guild_config[message.guild.id]['command_character'], '')
        params = list()

        if ' ' in command:
            command, params = (command.split()[0], command.split()[1:])

        command = command.lower()

        if command in self.commands:
            await self.commands[command].execute(CommandContext(self._bot, command, params, message))
        return
    
    async def disable_setup_button(self):
        """Disable setup button"""
        await self._game._setup_message.edit(view=create_br_button(self._bot, disabled=True))

    async def create_game(self, max_participants: int = 128) -> None:
        """Properly creates a game"""
        if self._game:
            self._game.game_director.stop()
        self._game = BRGame(self, max_participants)

    async def start_game_director(self) -> None:
        """Starts game director to manage the new BR."""
        self._game.game_director.start()

    async def stop_game_director(self) -> None:
        """Stops game director after game is over."""
        self._game.game_director.stop()

    async def timeout_user(self, user: dict) -> None:
        """Times the given user through discord feature and not a pit"""
        if user['member'].id in MOD_LIST:
            return
        timeout = datetime.datetime.utcnow() + datetime.timedelta(hours=min(self._game.round, 24))
        await user['member'].timeout(timeout, reason="Lost BR")

    def get_help(self, interaction: discord.Interaction) -> dict[str, Any]:
        """Returns a discord Embed in form of dictionary to display as help"""
        
        description = "BR module is a Battle Royale event where 128 people join and they get timed out with only one surviving."
        context = InteractionContext(self._bot, interaction)
        fields = [
            {'name': 'setup_br', 'value': f"{context.command_character}setup_br will set up the button to Join the BR.\r\n\r\n"+ 
                f"Example command: {context.command_character}setup_br", 'inline': False},
            {'name': 'start_br', 'value': f"{context.command_character}start_br will start the event.\r\n\r\n"+ 
                f"Example command: {context.command_character}start_br", 'inline': False},
            {'name': 'test_br', 'value': f"{context.command_character}test_br will start a test event.\r\n\r\n"+ 
                f"Example command: {context.command_character}test_br", 'inline': False},
        ]
        return {
            "title": "BR Module Help",
            "description": description,
            "fields": fields,
            "color": 0x0aeb06
        }
