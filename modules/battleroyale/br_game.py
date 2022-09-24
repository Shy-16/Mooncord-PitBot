# -*- coding: utf-8 -*-

## BR Game ##
# Hosts the logic and execution for each BR Game #

import logging
import random
import asyncio
from typing import Optional, List, Union, Dict, Any

from numpy.random import choice
from discord.ext import tasks

from .models.event import Event, events, weights
from .models.weapon import Fists

log: logging.Logger = logging.getLogger("br")


class BRGame:

    def __init__(self, parent,
                max_participants: Optional[int] = 128) -> None:

        # keep a pointer to parent just in case
        self._parent = parent

        # the discord message where people sign up
        self._setup_message: Dict[str, Any] = None

        # cooldown to edit the number of participants in the message
        self._edit_cd: bool = False

        # br related
        self.participants: List[dict] = list()
        self._max_participants: int = max_participants
        self._started: bool = False
        self._finished: bool = False
        self._round: int = 1

        self._friendships = list()
        self._enmity = list()

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
    @tasks.loop(seconds=30)
    async def game_director(self) -> None:
        """
        Handles any and all tasks related to mantaining the game
        """

        if self._finished:
            return

        if self._started:
            await self._generate_event()
            return

        if self._edit_cd:
            await self._update_message()


    async def _update_message(self) -> None:
        """
        Updates the message with current participants in the BR
        """

        # Change content and edit embed
        content = f"To join Battle Royale react with 👑\r\n\r\n\
        There are currently {len(self.participants)} / {self._max_participants} ready to battle."

        embed = self._setup_message['embeds'][0]
        embed['description'] = content

        payload = {
            'embeds': [embed]
        }

        await self._parent._bot.http.edit_message(self._setup_message['channel_id'], self._setup_message['id'], payload)
        self._edit_cd = 60

    def add_participant(self, member: dict) -> None:
        """
        Adds a member to the ongoing BR
        """

        # {'user': {'username': 'yuigahamayui', 'public_flags': 128, 'id': '539881999926689829', 'discriminator': '7441', 
        # 'avatar': '31f61997206954399620accc101c5928'}, 'roles': [...], 'premium_since': None, 'permissions': '4398046511103', 
        # 'pending': False, 'nick': 'yui', 'mute': False, 'joined_at': '2019-03-08T05:49:16.519000+00:00', 'is_pending': False, 'deaf': False, 
        # 'communication_disabled_until': None, 'avatar': None}

        br_member: dict = {
            'user_id': member['user']['id'],
            'username': member['user']['username'],
            'discriminator': member['user']['discriminator'],
            'nickname': member['nick'],
            'permissions': member['permissions'],
            'health': 10,
            'weapon': Fists(),
            'items': list()
        }

        self.participants.append(br_member)

    def has_participant(self, member: dict) -> bool:
        """
        Checks if the game already added a member
        """

        return member['user']['id'] in [x['user_id'] for x in self.participants]

    def get_participant(self) -> dict:
        """
        Gets a random participant
        """

        return random.choice(self.participants)

    def has_friendships(self, minimum: int = 1) -> bool:
        """
        Return if there are any friendships available.
        If minimum is provided it will check at least X friendships
        """

        return len(self._friendships) >= minimum

    def get_friendship(self, user: dict = None) -> List[dict]:
        """
        Return a random friendship.
        If user is given, return a friendship where the user is present.
        """

        if len(self._friendships) <= 0:
            return None

        if user:
            for fs in self._friendships:
                if user['user_id'] in [x['user_id'] for x in fs]:
                    return fs
            return None

        return random.choice(self._friendships)

    def get_friendships_sample(self, amount: int = 2) -> List[List[dict]]:
        """
        Gets a sample of X friendships from _friendships
        """

        return random.sample(self._friendships, amount)

    def get_friendship_with_users(self, amount: int = 2) -> List[dict]:
        """
        Gets a friendship with X amount of users
        """

        _fss = [fs for fs in self._friendships if len(fs) == amount]

        if not _fss:
            return list()

        return random.choice(_fss)

    def get_participant_or_friendship(self) -> Union[List[dict], dict]:
        """
        Draws a participant or friendship at random, from a pool of both
        """

        pool = self.participants + self._friendships

        return random.choice(pool)

    def draw_event(self) -> Event:
        """
        Draw an event from the pool and make sure it can be run
        """

        event = None
        _valid = False

        while not _valid:
            event = choice(events, size=1, replace=False, p=weights)[0]
            if event.players <= len(self.participants):
                _valid = True

        return event

    def run_event(self, all_losers: list, event: Event=None, players: list=None) -> dict:
        """
        Run an event and return a field to send to discord
        """

        # draw one event randomly from the pool
        if event:
            _event = event
        else:
            _event = self.draw_event()

        # execute event
        if players:
            _users, _template = _event.execute(self, players)
        else:
            _users, _template = _event.execute(self)

        # add losers and remove losers
        if _event.has_losers:
            all_losers.extend(_users)
            self.participants = [user for user in self.participants if user not in all_losers]

        # generate the field event
        return {'name': _event.name, 'value': _template, 'inline': False}

    # Functionality
    async def _generate_event(self) -> None:
        fields = []
        all_losers = []

        # Check how many people are left
        # 5 or more pull an event as always
        if len(self.participants) > 4:
            field = self.run_event(all_losers)
            fields.append(field)

            # if number of players left is greater than a set amount do more events, up to 3
            if len(self.participants) > 8:
                # draw another event
                field = self.run_event(all_losers)
                fields.append(field)

            # if number of players is greater than a set do one more
            if len(self.participants) > 16:
                # draw another event
                field = self.run_event(all_losers)
                fields.append(field)

            # print messages in chat
            fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
            await self._parent._bot.send_embed_message(self._setup_message['channel_id'], f"Round {self._round}", fields=fields)

            # sleep for 10 seconds then pit all losers
            await asyncio.sleep(10)

            for loser in all_losers:
                # Issue the timeout
                await self._parent.timeout_user(loser)

                # check and remove friendships with this user
                self._friendships = [friends for friends in self._friendships if friends[0] != loser and friends[1] != loser]

                # sleep for 2 seconds so we don't get rate limited
                await asyncio.sleep(2)

            # increase round by 1
            self._round += 1

        # 4 or less = do 2 events of duel.
        elif len(self.participants) in [3, 4]:
            if len(self.participants) == 4:
                split_1 = [self.participants[0], self.participants[1]]
                split_2 = [self.participants[2], self.participants[3]]
                field = self.run_event(all_losers, events[0], split_1)
                fields.append(field)
                field = self.run_event(all_losers, events[0], split_2)
                fields.append(field)
            else:
                field = self.run_event(all_losers, events[0], [self.participants[0], self.participants[1]])
                fields.append(field)

            fields.append({'name': 'Players', 'value': f'{len(self.participants)} players remaining.', 'inline': False})
            await self._parent._bot.send_embed_message(self._setup_message['channel_id'], f"Round {self._round}", fields=fields)

            # increase round by 1
            self._round += 1

        # 2 or less = do a duel and announce winner
        elif len(self.participants) <= 2:
            field = self.run_event(all_losers, events[0], [self.participants[0], self.participants[1]])
            fields.append(field)
            await self._parent._bot.send_embed_message(self._setup_message['channel_id'], f"Round {self._round}", fields=fields)

            # announce winner
            description= f'''
            Mooncord 2022 2nd edition Battle Royale Winner.

            <@{self.participants[0]['user_id']}>

            '''
            await self._parent._bot.send_embed_message(self._setup_message['channel_id'], "Battle Royale Winner", description)
            self._finished = True
