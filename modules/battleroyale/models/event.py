# -*- coding: utf-8 -*-

## Event Class ##
# Covers functionality for events during BR #

import random
from typing import Union, Tuple, List, Any

from .weapon import WEAPON_LIST
from .arena import Arena


class Encounter:
    @classmethod
    def get_team_power(cls, team: Union[dict, List[dict]]) -> int:
        """
        Returns weapon power for a team
        """

        power = 0
        if isinstance(team, list):
            for user in team:
                power += user['weapon'].power * user['weapon'].range
        else:
            power += team['weapon'].power * team['weapon'].range

        return power


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
            _weapons = [random.choice(list(WEAPON_LIST.items()))[1], random.choice(list(WEAPON_LIST.items()))[1]]

            _players[0]['weapon'] = _weapons[0]
            _players[1]['weapon'] = _weapons[1]

            # format template
            _template = f"<@{_players[0]['user_id']}> and <@{_players[1]['user_id']}> find a chest and loot it.\r\n \
            <@{_players[0]['user_id']}> finds a {_weapons[0].name} and <@{_players[1]['user_id']}> finds a {_weapons[1].name}"

        else:
            _player = game.get_participant()
            _weapon = random.choice(list(WEAPON_LIST.items()))[1]

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
        team_1_power = Encounter.get_team_power(team_1)
        team_2_power = Encounter.get_team_power(team_2)
        death = list()

        if isinstance(team_1, list):
            team_1_names = ",".join([f"<@{user['user_id']}>" for user in team_1[:-1]]) + " and " + team_1[-1]['user_id']

            if isinstance(team_2, list):
                team_2_names = ",".join([f"<@{user['user_id']}>" for user in team_2[:-1]]) + " and " + team_2[-1]['user_id']

                _template = f"Two teams clash in the field.\r\n" \
                    f"{team_1_names} cross with {team_2_names} {Arena.get_arena()}.\r\n\r\n"

                if team_1_power > team_2_power:
                    _template += f"<@{team_1[0]['user_id']}> {team_1[0]['weapon'].use()} <@{team_2[0]['user_id']}> {team_1[0]['weapon'].death()}"
                    _template += f"<@{team_1[1]['user_id']}> {team_1[1]['weapon'].use()} <@{team_2[1]['user_id']}> {team_1[1]['weapon'].death()}"
                    death.extend(team_2)

                elif team_1_power < team_2_power:
                    _template += f"<@{team_2[0]['user_id']}> {team_2[0]['weapon'].use()} <@{team_1[0]['user_id']}> {team_2[0]['weapon'].death()}"
                    _template += f"<@{team_2[1]['user_id']}> {team_2[1]['weapon'].use()} <@{team_1[1]['user_id']}> {team_2[1]['weapon'].death()}"
                    death.extend(team_1)

                else:
                    # roll a 1d3, 0 = tie, 1 = team_1, 2 = team_2
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"<@{team_1[0]['user_id']}> {team_1[0]['weapon'].use()} <@{team_2[0]['user_id']}> {team_1[0]['weapon'].death()}"
                        _template += f"<@{team_1[1]['user_id']}> {team_1[1]['weapon'].use()} <@{team_2[1]['user_id']}> {team_1[1]['weapon'].death()}"
                        death.extend(team_2)
                    else:
                        _template += f"<@{team_2[0]['user_id']}> {team_2[0]['weapon'].use()} <@{team_1[0]['user_id']}> {team_2[0]['weapon'].death()}"
                        _template += f"<@{team_2[1]['user_id']}> {team_2[1]['weapon'].use()} <@{team_1[1]['user_id']}> {team_2[1]['weapon'].death()}"
                        death.extend(team_1)

            else:
                _template = f"A team and a player cross paths on the battlefield.\r\n" \
                    f"{team_1_names} and <@{team_2['user_id']}> meet each other {Arena.get_arena()}.\r\n\r\n"

                if team_1_power > team_2_power:
                    _template += f"{team_1_names} surround <@{team_2['user_id']}> obliterating their existance."
                    death.append(team_2)

                elif team_1_power < team_2_power:
                    _template += f"<@{team_2['user_id']}> {team_2['weapon'].use()} {team_1_names} {team_2['weapon'].death()}"
                    death.extend(team_1)

                else:
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"{team_1_names} surround <@{team_2['user_id']}> obliterating their existance."
                    else:
                        _template += f"<@{team_2['user_id']}> {team_2['weapon'].use()} {team_1_names} {team_2['weapon'].death()}"

        else:
            if isinstance(team_2, list):
                team_2_names = ",".join([f"<@{user['user_id']}>" for user in team_2[:-1]]) + " and " + team_2[-1]['user_id']

                _template = f"A team and a player cross paths on the battlefield.\r\n\r" \
                    f"{team_2_names} and <@{team_1['user_id']}> meet each other {Arena.get_arena()}.\r\n\r\n"

                if team_2_power > team_1_power:
                    _template += f"{team_2_names} surround <@{team_1['user_id']}> obliterating their existance."
                    death.append(team_1)

                elif team_2_power < team_1_power:
                    _template += f"<@{team_1['user_id']}> {team_1['weapon'].use()} {team_2_names} {team_1['weapon'].death()}"
                    death.extend(team_2)

                else:
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"<@{team_1['user_id']}> {team_1['weapon'].use()} {team_2_names} {team_1['weapon'].death()}"
                        death.extend(team_2)
                    else:
                        _template += f"{team_2_names} surround <@{team_1['user_id']}> obliterating their existance."
                        death.append(team_1)
            else:
                _template = f"Two players cross paths on the battlefield.\r\n" \
                    f"<@{team_1['user_id']}> and <@{team_2['user_id']}> meet each other {Arena.get_arena()}.\r\n\r\n"

                if team_1_power > team_2_power:
                    _template += f"<@{team_1['user_id']}> {team_1['weapon'].use()} <@{team_2['user_id']}> {team_1['weapon'].death()}"
                    death.append(team_2)

                elif team_1_power < team_2_power:
                    _template += f"<@{team_2['user_id']}> {team_2['weapon'].use()} <@{team_1['user_id']}> {team_2['weapon'].death()}"
                    death.append(team_1)

                else:
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"<@{team_1['user_id']}> {team_1['weapon'].use()} <@{team_2['user_id']}> {team_1['weapon'].death()}"
                        death.append(team_2)
                    else:
                        _template += f"<@{team_2['user_id']}> {team_2['weapon'].use()} <@{team_1['user_id']}> {team_2['weapon'].death()}"
                        death.append(team_1)

        return (death, _template)


class Sponsor(Event):
    """
    Sponsor gives a chest and find a Weapon. Maybe items at some point
    """

    def __init__(self):
        super().__init__("Loot", 1, False)

    def execute(self, game, players=None):

        if game.has_friendships():
            self.players = 2

        draw = random.randint(1, self.players)

        if draw == 2:
            _players = game.get_friendship_with_users()
            _weapons = [random.choice(list(WEAPON_LIST.items()))[1], random.choice(list(WEAPON_LIST.items()))[1]]

            _players[0]['weapon'] = _weapons[0]
            _players[1]['weapon'] = _weapons[1]

            # format template
            _template = f"A 3rd party sponsor has involved in a bet of very large amount of money and to make sure they don't lose, " \
                f"they have sponsored <@{_players[0]['user_id']}> and <@{_players[1]['user_id']}> with a chest.\r\n " \
                f"<@{_players[0]['user_id']}> gets a {_weapons[0].name} and <@{_players[1]['user_id']}> gets a {_weapons[1].name}!"

        else:
            _player = game.get_participant()
            _weapon = random.choice(list(WEAPON_LIST.items()))[1]
            _weapon = random.choice(list(WEAPON_LIST.items()))[1]

            _player['weapon'] = _weapon

            # format template
            _template = f"A 3rd party sponsor has involved in a bet of very large amount of money and to make sure they don't lose, " \
                f"they have sponsored <@{_player['user_id']}> with a chest.\r\n"  \
                f"They find a {_weapon.name} inside!"

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
            
        team_1 = _players[0]
        team_2 = _players[1]
        team_1_power = Encounter.get_team_power(team_1)
        team_2_power = Encounter.get_team_power(team_2)
        death = list()
            
        _template = f"Two players cross paths on the battlefield.\r\n" \
                    f"<@{team_1['user_id']}> and <@{team_2['user_id']}> meet each other {Arena.get_arena()}.\r\n\r\n"

        if team_1_power > team_2_power:
            _template += f"<@{team_1['user_id']}> {team_1['weapon'].use()} <@{team_2['user_id']}> {team_1['weapon'].death()}"
            death.append(team_2)

        elif team_1_power < team_2_power:
            _template += f"<@{team_2['user_id']}> {team_2['weapon'].use()} <@{team_1['user_id']}> {team_2['weapon'].death()}"
            death.append(team_1)

        else:
            winner = random.randint(1, 2)
            if winner == 1:
                _template += f"<@{team_1['user_id']}> {team_1['weapon'].use()} <@{team_2['user_id']}> {team_1['weapon'].death()}"
                death.append(team_2)
            else:
                _template += f"<@{team_2['user_id']}> {team_2['weapon'].use()} <@{team_1['user_id']}> {team_2['weapon'].death()}"
                death.append(team_1)

        return (death, _template)


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
            _template = f"<@{_players[0]['user_id']}>, <@{_players[1]['user_id']}>, <@{_players[2]['user_id']}> and <@{_players[3]['user_id']}> " \
                "cross each other in the battlefield.\r\n" \
                f"<@{_winners[0]['user_id']}>, <@{_winners[1]['user_id']}> and <@{_winners[2]['user_id']}> gang around <@{_losers[0]['user_id']}> " \
                "and beat them to death."

        elif total_losers == 2:
            _template = f"<@{_players[0]['user_id']}>, <@{_players[1]['user_id']}>, <@{_players[2]['user_id']}> and <@{_players[3]['user_id']}> " \
                "cross each other in the battlefield.\r\n" \
                f"<@{_winners[0]['user_id']}> and <@{_winners[1]['user_id']}> look at each other and form an alliance, bringing a bloodshed upon " \
                f"<@{_losers[0]['user_id']}> and <@{_losers[1]['user_id']}>."

        else:
            _template = f"<@{_players[0]['user_id']}>, <@{_players[1]['user_id']}>, <@{_players[2]['user_id']}> and <@{_players[3]['user_id']}> " \
                "cross each other in the battlefield.\r\n" \
                f"<@{_winners[0]['user_id']}> hides in a bush and skillfully aiming his sniper rifle headshots <@{_losers[0]['user_id']}>, " \
                f"<@{_losers[1]['user_id']}> and <@{_losers[2]['user_id']}>."

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
        _template = f"<@{_players[0]['user_id']}> and <@{_players[1]['user_id']}> have decided to team up to have better chances to win."

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
        _template = f"<@{_winner['user_id']}> sees an opening and stabs <@{_loser['user_id']}> in the back."

        return ([_loser], _template)


class Accident(Event):

    ACCIDENTS = {
        "single": [
            "<@{}> tripped on a branch and fell into the ground snapping their neck.",
            "<@{}> tried jumping over a fence and got electrocuted to death.",
            "<@{}> stepped on a landmine and was blown into a thousand pieces.",
            "<@{}> was struck by a thunder and instantly died.",
            "A wild bear chased <@{}> and ripped their guts out.",
        ],
        "multiple": [
            "<@{}> and <@{}> tripped on a branch and fell into the ground snapping their necks.",
            "<@{}> and <@{}> tried jumping over a fence and got electrocuted to death.",
            "<@{}> and <@{}> stepped on a landmine and were blown into a thousand pieces.",
            "<@{}> and <@{}> were struck by a thunder and instantly died.",
            "A wild bear chased <@{}> and <@{}> and ripped their guts out.",
        ]
    }

    def __init__(self):
        super().__init__("Accident", 2)

    def execute(self, game):
        _loser = game.get_participant_or_friendship()

        # generate template
        if isinstance(_loser, list):
            return (_loser, random.choice(self.ACCIDENTS["multiple"]).format(*[l['user_id'] for l in _loser]))
        else:
            return (_loser, random.choice(self.ACCIDENTS["single"]).format(_loser['user_id']))


events = [
    Kill(),
    Duel2(),
    Duel4(),
    Friendship(),
    Betrayal(),
    Accident(),
    Loot(),
    Sponsor()
]

weights = [
    0.175,
    0.175,
    0.175,
    0.125,
    0.125,
    0.075,
    0.075,
    0.075
]