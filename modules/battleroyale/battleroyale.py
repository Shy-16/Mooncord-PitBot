# -*- coding: utf-8 -*-

## Roulette Module ##
# Fluff roulette minigame where people gamble a pit #

import logging
import datetime
from typing import Optional, List, Dict, Any

import discord
from discord.ext import tasks

from utils import MOD_LIST
from modules.command import Command
from modules.context import CommandContext
from .commands import SetupBRCommand, StartBRCommand, TestBRCommand
from .components import handle_join_br_button
from .br_game import BRGame

log: logging.Logger = logging.getLogger("br")


class BattleRoyale:

    DEFAULT_MAX_PARTICIPANTS = 128

    def __init__(self, *, bot: discord.Client) -> None:
        """
        :var bot discord.Client: The bot instance
        """

        self._bot: discord.Client = bot

        self._game: BRGame = None

        self.commands: Dict[str, Command] = {
            "setup_br": SetupBRCommand(self, 'mod'),
            "start_br": StartBRCommand(self, 'mod'),
            "test_br": TestBRCommand(self, 'mod')
        }

    @property
    def game(self):
        return self._game

    def init_tasks(self) -> None:
        """
        Initialize the different tasks that run in the background
        """

        handle_join_br_button(self._bot)

    async def handle_commands(self, message: discord.Context) -> None:
        """
        Handles any commands given through the designed character
        """

        command = message.content.replace(self._bot.guild_config[message.guild_id]['command_character'], '')
        params = list()

        if ' ' in command:
            command, params = (command.split()[0], command.split()[1:])

        command = command.lower()

        if command in self.commands:
            await self.commands[command].execute(CommandContext(self._bot, command, params, message))
        return

    @tasks.loop(minutes=1)
    async def game_watcher(self) -> None:
        """
        This function will watch the state of an ongoing game
        and perform maintenance tasks as required
        """

        if self._game:
            pass

    async def disable_setup_button(self) -> None:
        """
        Disables the setup button
        """

        # disable button so players can't join after it starts
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

        await self._bot.http.edit_message(self._game._setup_message['channel_id'], self._game._setup_message['id'], payload)

    async def create_game(self, max_participants: Optional[int] = 128) -> None:
        """
        Properly creates a game
        """

        if self._game:
            # remove any ongoing tasks
            self._game.game_director.stop()

            # any other cleanup?

        self._game = BRGame(self, max_participants)

    async def start_game_director(self) -> None:
        """
        Starts game director to manage the new BR.
        """

        # Start game director
        self._game.game_director.start()

    async def stop_game_director(self) -> None:
        """
        Stops game director after game is over.
        """

        # Stop game director
        self._game.game_director.stop()

    async def timeout_user(self, user_id: str) -> None:
        """
        Times the given user through discord feature and not a pit
        """

        # don't hate me for hardcoding this
        guild_id = '193277318494420992'

        # mods cannot be timed out, so if the user is a mod skip.
        if user_id in MOD_LIST:
            return

        timeout = (datetime.datetime.utcnow() + datetime.timedelta(hours=min(self._round, 24))).isoformat()
        data = {'communication_disabled_until': timeout}

        response = await self._bot.http.modify_member(user_id, guild_id, data)
