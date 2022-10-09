# -*- coding: utf-8 -*-

## BR Game ##
# Hosts the logic and execution for each BR Game #

import logging
import random
import asyncio
from typing import Optional, List, Union

from numpy.random import choice
import discord
from discord.ext import tasks

from .models.event import (
    Event,
    Kill,
    Duel2,
    Friendship,
    FinalRomance,
    kill_events,
    kill_weights,
    friend_events,
    friend_weights,
    loot_events,
    loot_weights,
    low_kill_events,
    low_kill_weights
)
from .models.weapon import Fists

log: logging.Logger = logging.getLogger("br")


class BRGame:
    def __init__(self, parent, max_participants: Optional[int] = 128) -> None:
        self._parent = parent

        # the discord message where people sign up
        self._setup_message: discord.Message = None
        self._edit_cd: bool = False

        # br related
        self.participants: List[dict] = []
        self._max_participants: int = max_participants
        self._started: bool = False
        self._finished: bool = False
        self._round: int = 1

        self._friendships = []
        self._enmity = []

    @property
    def max_participants(self) -> int:
        return self._max_participants

    @property
    def started(self) -> bool:
        return self._started

    @property
    def finished(self):
        return self._finished

    @property
    def round(self) -> int:
        return self._round

    # Setup the task to edit entries
    @tasks.loop(seconds=20)
    async def game_director(self) -> None:
        """Handles any and all tasks related to mantaining the game"""
        if self._finished:
            return
        if self._started:
            await self._generate_event()
            return
        if self._edit_cd:
            await self._update_message()

    async def _update_message(self) -> None:
        """Updates the message with current participants in the BR"""
        content = f"To join Battle Royale react with 👑\r\n\r\n\
        There are currently {len(self.participants)} / {self._max_participants} ready to battle."

        embed = self._setup_message.embeds[0]
        embed.description = content
        await self._setup_message.edit(embed=embed)

    def add_participant(self, member: discord.User) -> None:
        """Adds a member to the ongoing BR"""
        br_member: dict = {
            'member': member,
            'health': 10,
            'weapon': Fists(),
            'items': list()
        }
        self.participants.append(br_member)

    def has_participant(self, member: discord.User) -> bool:
        """Checks if the game already added a member"""
        return member in [x['member'] for x in self.participants]

    def get_participant(self) -> dict:
        """Gets a random participant"""
        return random.choice(self.participants)

    def has_friendships(self, minimum: int = 1) -> bool:
        """
        Return if there are any friendships available.
        If minimum is provided it will check at least X friendships
        """
        return len(self._friendships) >= minimum

    def get_friendship(self, user: discord.User = None) -> List[dict]:
        """
        Return a random friendship.
        If user is given, return a friendship where the user is present.
        """

        if len(self._friendships) <= 0:
            return None

        if user:
            for fs in self._friendships:
                if user['member'] in [x['member'] for x in fs]:
                    return fs
            return None

        return random.choice(self._friendships)

    def get_friendships_sample(self, amount: int = 2) -> List[List[dict]]:
        """Gets a sample of X friendships from _friendships"""
        return random.sample(self._friendships, amount)

    def get_friendship_with_users(self, amount: int = 2) -> List[dict]:
        """Gets a friendship with X amount of users"""
        _fss = [fs for fs in self._friendships if len(fs) == amount]
        if not _fss:
            return list()
        return random.choice(_fss)

    def get_participant_or_friendship(self) -> Union[List[dict], dict]:
        """Draws a participant or friendship at random, from a pool of both"""
        pool = self.participants + self._friendships
        return random.choice(pool)

    def draw_event(self, pool: list, weights: list) -> Event:
        """Draw an event from the pool and make sure it can be run"""
        event = None
        _valid = False
        while not _valid:
            event = choice(pool, size=1, replace=False, p=weights)[0]
            if event.players <= len(self.participants):
                _valid = True
        return event

    def run_event(self, all_losers: list, event: Event=None, players: list=None) -> dict:
        """Run an event and return a field to send to discord"""
        if players:
            _users, _template = event.execute(self, players)
        else:
            _users, _template = event.execute(self)

        if event.has_losers:
            all_losers.extend(_users)
            self.participants = [user for user in self.participants if user not in all_losers]
        return {'name': event.name, 'value': _template, 'inline': False}

    # Functionality
    async def _generate_event(self) -> None:
        fields = []
        all_losers = []

        # Check how many people are left
        # 8 or more we pull 4 events
        if len(self.participants) >= 64:
            # draw 4 kill, 2 friendship and 2 loot event
            kill_event = self.draw_event(kill_events, kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            kill_event = self.draw_event(kill_events, kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            kill_event = self.draw_event(kill_events, kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            kill_event = self.draw_event(kill_events, kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            # draw a friendship event
            friendship = self.get_friendship()
            if friendship is None:
                fields.append(self.run_event(all_losers, Friendship()))
                fields.append(self.run_event(all_losers, Friendship()))
            else:
                friendship_event = self.draw_event(friend_events, friend_weights)
                fields.append(self.run_event(all_losers, friendship_event))
            # draw a loot event
            loot_event = self.draw_event(loot_events, loot_weights)
            fields.append(self.run_event(all_losers, loot_event))
            loot_event = self.draw_event(loot_events, loot_weights)
            fields.append(self.run_event(all_losers, loot_event))
            
            fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
            await self._parent._bot.send_embed_message(self._setup_message.channel, f"Round {self._round}", fields=fields)
            
            await asyncio.sleep(5)
            for loser in all_losers:
                await self._parent.timeout_user(loser)
                self._friendships = [friends for friends in self._friendships if friends[0] != loser and friends[1] != loser]
                await asyncio.sleep(1)
            self._round += 1

        # 8 or more we pull 4 events
        if len(self.participants) >= 8:
            # draw 2 kill, 1 friendship and 1 loot event
            kill_event = self.draw_event(kill_events, kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            kill_event = self.draw_event(kill_events, kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            # draw a friendship event
            friendship = self.get_friendship()
            if friendship is None:
                fields.append(self.run_event(all_losers, Friendship()))
            else:
                friendship_event = self.draw_event(friend_events, friend_weights)
                fields.append(self.run_event(all_losers, friendship_event))
            # draw a loot event
            loot_event = self.draw_event(loot_events, loot_weights)
            fields.append(self.run_event(all_losers, loot_event))
            
            fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
            await self._parent._bot.send_embed_message(self._setup_message.channel, f"Round {self._round}", fields=fields)
            
            await asyncio.sleep(5)
            for loser in all_losers:
                await self._parent.timeout_user(loser)
                self._friendships = [friends for friends in self._friendships if friends[0] != loser and friends[1] != loser]
                await asyncio.sleep(1)
            self._round += 1
            
        # 4 or more we pull only 2 kill
        elif len(self.participants) >= 4:
            kill_event = self.draw_event(low_kill_events, low_kill_weights)
            fields.append(self.run_event(all_losers, kill_event))
            kill_event = self.draw_event(low_kill_events, low_kill_weights)
            fields.append(self.run_event(all_losers, kill_event))

            fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
            await self._parent._bot.send_embed_message(self._setup_message.channel, f"Round {self._round}", fields=fields)

            await asyncio.sleep(5)
            for loser in all_losers:
                await self._parent.timeout_user(loser)
                self._friendships = [friends for friends in self._friendships if friends[0] != loser and friends[1] != loser]
                await asyncio.sleep(1)
            self._round += 1
            
        # if 3 only create a kill event
        elif len(self.participants) == 3:
            fields.append(self.run_event(all_losers, Kill()))

            fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
            await self._parent._bot.send_embed_message(self._setup_message.channel, f"Round {self._round}", fields=fields)

            await asyncio.sleep(5)
            for loser in all_losers:
                await self._parent.timeout_user(loser)
                self._friendships = [friends for friends in self._friendships if friends[0] != loser and friends[1] != loser]
                await asyncio.sleep(1)
            self._round += 1

        # 2 or less = do a duel and announce winner
        elif len(self.participants) <= 2:
            if len(self._friendships) == 1:
                friendship = self._friendships[0]
                fields.append(self.run_event(all_losers, FinalRomance(), friendship))
            else:
                fields.append(self.run_event(all_losers, Duel2(), [self.participants[0], self.participants[1]]))

            await self._parent._bot.send_embed_message(self._setup_message.channel, f"Round {self._round}", fields=fields)
            # announce winner
            description= f'''
            Mooncord 2022 Halloween Edition Battle Royale Winner.

            <@{self.participants[0]['member'].id}>

            '''
            await self._parent._bot.send_embed_message(self._setup_message.channel, "Battle Royale Winner", description)
            self._finished = True
