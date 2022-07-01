# -*- coding: utf-8 -*-

## Event Class ##
# Covers functionality for events during BR #

import random
from typing import Tuple, List, Any

from .weapon import WEAPON_LIST


class Arena:
    OPEN_FIELD: str = 'an open field'
    FOREST: str = 'a forest'
    TUNNEL: str = 'a tunnel'
    HOUSE: str = 'a house'
    TOWER: str = 'a tower'

    KEYS = [OPEN_FIELD, FOREST, TUNNEL, HOUSE, TOWER]

    @classmethod
    def get_arena(cls) -> str:
        """
        Returns an arena
        """

        arena = random.choice(cls.KEYS)

        return f'in {arena}'


class Encounter:
    @classmethod
    def win(cls, winner: dict, loser: dict) -> str:
        """
        Generates a beutified string for a clash
        """

        _template: str = f"<@{winner['user_id']}> "

        return _template

    @classmethod
    def draw(cls, first: dict, second: dict) -> str:
        """
        Generates a beutified string for a clash
        """

        _template: str = f"<@{first['user_id']}> "

        return _template


class Event:

    def __init__(self, name, players=4, has_losers=True):

        self.name = name
        self.players = players
        self.has_losers = has_losers

    def execute(self, game, players: int = None) -> Tuple[List[dict], str]:
        """
        Execute the event
        """
        pass


class Loot(Event):
    """
    Open a chest and find a Weapon. Maybe items at some point
    """

    def __init__(self):
        super().__init__("Loot", 1, False)

    def execute(self, game, players=None):

        if game.has_friendships():
            self.players = 2

        draw = random.randint(1, self.players)

        if draw == 2:
            _players = game.get_friendship_with_users()
            _weapons = random.sample(WEAPON_LIST, 2)

            _players[0]['weapon'] = _weapons[0]
            _players[1]['weapon'] = _weapons[1]

            # format template
            _template = f"<@{_players[0]['user_id']}> and <@{_players[1]['user_id']}> find a chest and loot it.\r\n \
            <@{_players[0]['user_id']}> finds a {_weapons[0].name} and <@{_players[1]['user_id']}> finds a {_weapons[1].name}"

        else:
            _player = game.get_participant()
            _weapon = random.choice(WEAPON_LIST)

            _player['weapon'] = _weapon

            # format template
            _template = f"<@{_player['user_id']}> finds a chest and loots it. They find a {_weapon.name} inside."

        return ([], _template)


class Kill(Event):
    """
    A player or players get a kill on someone or someones.
    """

    def __init__(self):
        super().__init__("Kill", 1)

    def execute(self, game, players=None):

        _allow_friendships = game.has_friendships(minimum=2)

        team_1 = game.get_participant_or_friendship() if _allow_friendships else game.get_participant()
        team_2 = game.get_participant_or_friendship() if _allow_friendships else game.get_participant()
        death = list()

        if isinstance(team_1, list):
            team_1_names = ",".join([f"<@{user['user_id']}>" for user in team_1[:-1]]) + " and " + team_1[-1]['user_id']

            if isinstance(team_2, list):
                team_2_names = ",".join([f"<@{user['user_id']}>" for user in team_2[:-1]]) + " and " + team_2[-1]['user_id']

                _template = f"Two teams clash in the field.\r\n\r\n"+
                f"{team_1_names} cross with {team_2_names} {Arena.get_arena()}"

                # handle first 2 members, this is granted
                if team_1[0]['weapon'] == team_2[0]['weapon']:
                    Encounter.draw(team_1[0], team_2[0])

                elif team_1[0]['weapon'] > team_2[0]['weapon']:
                    Encounter.win(team_1[0], team_2[0])
                    death.append(team_2[0])

                else:
                    Encounter.win(team_2[0], team_1[0])
                    death.append(team_1[0])

        else:
            _player = game.get_participant()

        return ([], _template)


class Duel2(Event):

    def __init__(self):
        super().__init__("Duel", 2)

    def execute(self, game, players=None):

        # choose 2 players
        if players:
            _players = players
        else:
            _players = random.sample(game.participants, self.players)

        # choose a loser
        _loser = random.choice(_players)

        # format template
        _template = f"<@{_players[0]}> and <@{_players[1]}> cross each other in the battlefield.\r\n \
        <@{_loser}> gets mercilessly stabbed in the heart to death."

        return ([_loser], _template)


class Duel4(Event):

    def __init__(self):
        super().__init__("Duel", 4)

    def execute(self, game, players=None):

        # choose 4 players
        if players:
            _players = players
        else:
            _players = random.sample(game.participants, self.players)

        # choose how many losers there are
        total_losers = random.randint(1, self.players-1)

        # get losers
        _losers = random.sample(_players, total_losers)
        _winners = [x for x in _players if x not in _losers]

        # generate template
        _template = ""

        if total_losers == 1:
            _template = f"<@{_players[0]}>, <@{_players[1]}>, <@{_players[2]}> and <@{_players[3]}> cross each other in the battlefield.\r\n \
            <@{_winners[0]}>, <@{_winners[1]}> and <@{_winners[2]}> gang around <@{_losers[0]}> and beat them to death."

        elif total_losers == 2:
            _template = f"<@{_players[0]}>, <@{_players[1]}>, <@{_players[2]}> and <@{_players[3]}> cross each other in the battlefield.\r\n \
            <@{_winners[0]}> and <@{_winners[1]}> look at each other and form an alliance, bringing a bloodshed upon <@{_losers[0]}> and <@{_losers[1]}>."

        else:
            _template = f"<@{_players[0]}>, <@{_players[1]}>, <@{_players[2]}> and <@{_players[3]}> cross each other in the battlefield.\r\n \
            <@{_winners[0]}> hides in a bush and skillfully aiming his sniper rifle headshots <@{_losers[0]}>, <@{_losers[1]}> and <@{_losers[2]}>."

        return (_losers, _template)


class Friendship(Event):

    def __init__(self):
        super().__init__("Friendship", 2, False)

    def execute(self, game):

        # choose 2 players
        all_friendships = [user for friendship in game._friendships for user in friendship]
        _players = random.sample([user for user in game.participants if user not in all_friendships], self.players)

        # generate friendship
        game._friendships.append(_players)

        # generate template
        _template = f"<@{_players[0]}> and <@{_players[1]}> have decided to team up to have better chances to win."

        return (_players, _template)


class Betrayal(Event):

    def __init__(self):
        super().__init__("Betrayal", 2)

    def execute(self, game):

        # choose 2 players
        if len(game._friendships) <= 0:
            _template = "There are no betrayals today."
            return ([], _template)

        _players = random.choice(game._friendships)

        # choose a loser
        _loser = random.choice(_players)
        _winner = _players[0] if _players[0] != _loser else _players[1]

        # generate template
        _template = f"<@{_winner}> sees an opening and stabs <@{_loser}> in the back."

        return ([_loser], _template)


events = [
    Duel2(),
    Duel4(),
    Friendship(),
    Betrayal()
]

weights = [
    0.4,
    0.4,
    0.1,
    0.1
]