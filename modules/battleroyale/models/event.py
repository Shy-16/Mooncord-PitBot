# -*- coding: utf-8 -*-

## Event Class ##
# Covers functionality for events during BR #

import random
from typing import Union, Tuple, List

from numpy.random import choice

from .weapon import WEAPON_LIST, WEAPON_WEIGHTS, SPONSOR_LIST, SPONSOR_WEIGHTS
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
        """Execute the event"""


class Kill(Event):
    """A player or players get a kill on someone or someones."""
    def __init__(self):
        super().__init__("Kill", 1)

    def execute(self, game, players=None):
        _allow_friendships = game.has_friendships(minimum=2)

        team_1 = game.get_participant_or_friendship() if _allow_friendships else game.get_participant()
        team_2 = game.get_participant_or_friendship() if _allow_friendships else game.get_participant()
        if team_1 == team_2:
            # chances this happening twice in a row are so low I don't care, if it happens then we laugh
            team_2 = game.get_participant_or_friendship() if _allow_friendships else game.get_participant()
        team_1_power = Encounter.get_team_power(team_1)
        team_2_power = Encounter.get_team_power(team_2)
        death = list()

        if isinstance(team_1, list):
            team_1_names = ",".join([f"<@{user['member'].id}>" for user in team_1[:-1]]) + " and " + str(team_1[-1]['member'].id)

            if isinstance(team_2, list):
                team_2_names = ",".join([f"<@{user['member'].id}>" for user in team_2[:-1]]) + " and " + str(team_2[-1]['member'].id)

                _template = f"Two teams clash in the field.\r\n" \
                    f"{team_1_names} cross with {team_2_names} {Arena.get_arena()}.\r\n\r\n"

                if team_1_power > team_2_power:
                    _template += f"<@{team_1[0]['member'].id}> {team_1[0]['weapon'].use()} <@{team_2[0]['member'].id}> {team_1[0]['weapon'].death()}"
                    _template += f"<@{team_1[1]['member'].id}> {team_1[1]['weapon'].use()} <@{team_2[1]['member'].id}> {team_1[1]['weapon'].death()}"
                    death.extend(team_2)

                elif team_1_power < team_2_power:
                    _template += f"<@{team_2[0]['member'].id}> {team_2[0]['weapon'].use()} <@{team_1[0]['member'].id}> {team_2[0]['weapon'].death()}"
                    _template += f"<@{team_2[1]['member'].id}> {team_2[1]['weapon'].use()} <@{team_1[1]['member'].id}> {team_2[1]['weapon'].death()}"
                    death.extend(team_1)

                else:
                    # roll a 1d3, 0 = tie, 1 = team_1, 2 = team_2
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"<@{team_1[0]['member'].id}> {team_1[0]['weapon'].use()} <@{team_2[0]['member'].id}> {team_1[0]['weapon'].death()}"
                        _template += f"<@{team_1[1]['member'].id}> {team_1[1]['weapon'].use()} <@{team_2[1]['member'].id}> {team_1[1]['weapon'].death()}"
                        death.extend(team_2)
                    else:
                        _template += f"<@{team_2[0]['member'].id}> {team_2[0]['weapon'].use()} <@{team_1[0]['member'].id}> {team_2[0]['weapon'].death()}"
                        _template += f"<@{team_2[1]['member'].id}> {team_2[1]['weapon'].use()} <@{team_1[1]['member'].id}> {team_2[1]['weapon'].death()}"
                        death.extend(team_1)

            else:
                _template = f"A team and a player cross paths on the battlefield.\r\n" \
                    f"{team_1_names} and <@{team_2['member'].id}> meet each other {Arena.get_arena()}.\r\n\r\n"

                if team_1_power > team_2_power:
                    _template += f"{team_1_names} surround <@{team_2['member'].id}> obliterating their existance."
                    death.append(team_2)

                elif team_1_power < team_2_power:
                    _template += f"<@{team_2['member'].id}> {team_2['weapon'].use()} {team_1_names} {team_2['weapon'].death()}"
                    death.extend(team_1)

                else:
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"{team_1_names} surround <@{team_2['member'].id}> obliterating their existance."
                    else:
                        _template += f"<@{team_2['member'].id}> {team_2['weapon'].use()} {team_1_names} {team_2['weapon'].death()}"

        else:
            if isinstance(team_2, list):
                team_2_names = ",".join([f"<@{user['member'].id}>" for user in team_2[:-1]]) + " and " + str(team_2[-1]['member'].id)

                _template = f"A team and a player cross paths on the battlefield.\r\n\r" \
                    f"{team_2_names} and <@{team_1['member'].id}> meet each other {Arena.get_arena()}.\r\n\r\n"

                if team_2_power > team_1_power:
                    _template += f"{team_2_names} surround <@{team_1['member'].id}> obliterating their existance."
                    death.append(team_1)

                elif team_2_power < team_1_power:
                    _template += f"<@{team_1['member'].id}> {team_1['weapon'].use()} {team_2_names} {team_1['weapon'].death()}"
                    death.extend(team_2)

                else:
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"<@{team_1['member'].id}> {team_1['weapon'].use()} {team_2_names} {team_1['weapon'].death()}"
                        death.extend(team_2)
                    else:
                        _template += f"{team_2_names} surround <@{team_1['member'].id}> obliterating their existance."
                        death.append(team_1)
            else:
                _template = f"Two players cross paths on the battlefield.\r\n" \
                    f"<@{team_1['member'].id}> and <@{team_2['member'].id}> meet each other {Arena.get_arena()}.\r\n\r\n"

                if team_1_power > team_2_power:
                    _template += f"<@{team_1['member'].id}> {team_1['weapon'].use()} <@{team_2['member'].id}> {team_1['weapon'].death()}"
                    death.append(team_2)

                elif team_1_power < team_2_power:
                    _template += f"<@{team_2['member'].id}> {team_2['weapon'].use()} <@{team_1['member'].id}> {team_2['weapon'].death()}"
                    death.append(team_1)

                else:
                    winner = random.randint(0, 2)
                    if winner == 0:
                        _template += "They scout their weapons and decide it's not worth to fight, parting ways in different directions."
                    elif winner == 1:
                        _template += f"<@{team_1['member'].id}> {team_1['weapon'].use()} <@{team_2['member'].id}> {team_1['weapon'].death()}"
                        death.append(team_2)
                    else:
                        _template += f"<@{team_2['member'].id}> {team_2['weapon'].use()} <@{team_1['member'].id}> {team_2['weapon'].death()}"
                        death.append(team_1)

        return (death, _template)


class Duel2(Event):
    def __init__(self):
        super().__init__("Duel", 2)

    def execute(self, game, players=None):
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
                    f"<@{team_1['member'].id}> and <@{team_2['member'].id}> meet each other {Arena.get_arena()}.\r\n\r\n"

        if team_1_power > team_2_power:
            _template += f"<@{team_1['member'].id}> {team_1['weapon'].use()} <@{team_2['member'].id}> {team_1['weapon'].death()}"
            death.append(team_2)

        elif team_1_power < team_2_power:
            _template += f"<@{team_2['member'].id}> {team_2['weapon'].use()} <@{team_1['member'].id}> {team_2['weapon'].death()}"
            death.append(team_1)

        else:
            winner = random.randint(1, 2)
            if winner == 1:
                _template += f"<@{team_1['member'].id}> {team_1['weapon'].use()} <@{team_2['member'].id}> {team_1['weapon'].death()}"
                death.append(team_2)
            else:
                _template += f"<@{team_2['member'].id}> {team_2['weapon'].use()} <@{team_1['member'].id}> {team_2['weapon'].death()}"
                death.append(team_1)

        return (death, _template)


class Duel4(Event):
    def __init__(self):
        super().__init__("Duel", 4)

    def execute(self, game, players=None):
        if players:
            _players = players
        else:
            _players = random.sample(game.participants, self.players)

        total_losers = random.randint(1, self.players-1)
        _losers = random.sample(_players, total_losers)
        _winners = [x for x in _players if x not in _losers]
        _template = ""

        if total_losers == 1:
            _template = f"<@{_players[0]['member'].id}>, <@{_players[1]['member'].id}>, <@{_players[2]['member'].id}> and <@{_players[3]['member'].id}> " \
                "cross each other in the battlefield.\r\n" \
                f"<@{_winners[0]['member'].id}>, <@{_winners[1]['member'].id}> and <@{_winners[2]['member'].id}> gang around <@{_losers[0]['member'].id}> " \
                "and beat them to death."

        elif total_losers == 2:
            _template = f"<@{_players[0]['member'].id}>, <@{_players[1]['member'].id}>, <@{_players[2]['member'].id}> and <@{_players[3]['member'].id}> " \
                "cross each other in the battlefield.\r\n" \
                f"<@{_winners[0]['member'].id}> and <@{_winners[1]['member'].id}> look at each other and form an alliance, bringing a bloodshed upon " \
                f"<@{_losers[0]['member'].id}> and <@{_losers[1]['member'].id}>."

        else:
            _template = f"<@{_players[0]['member'].id}>, <@{_players[1]['member'].id}>, <@{_players[2]['member'].id}> and <@{_players[3]['member'].id}> " \
                "cross each other in the battlefield.\r\n" \
                f"<@{_winners[0]['member'].id}> hides in a bush and skillfully aiming his sniper rifle headshots <@{_losers[0]['member'].id}>, " \
                f"<@{_losers[1]['member'].id}> and <@{_losers[2]['member'].id}>."

        return (_losers, _template)


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

    def execute(self, game, players=None):
        _loser = game.get_participant_or_friendship()
        if isinstance(_loser, list):
            return (_loser, random.choice(self.ACCIDENTS["multiple"]).format(*[l['member'].id for l in _loser]))
        else:
            return ([_loser], random.choice(self.ACCIDENTS["single"]).format(_loser['member'].id))


class Loot(Event):
    """Open a chest and find a Weapon. Maybe items at some point"""
    def __init__(self):
        super().__init__("Loot", 1, False)

    def execute(self, game, players=None):
        if game.has_friendships():
            self.players = 2

        draw = random.randint(1, self.players)

        if draw == 2:
            _players = game.get_friendship_with_users()
            _weapons = choice([y for _, y in WEAPON_LIST.items()], size=2, replace=False, p=WEAPON_WEIGHTS)
            _players[0]['weapon'] = _weapons[0]
            _players[1]['weapon'] = _weapons[1]
            _template = f"<@{_players[0]['member'].id}> and <@{_players[1]['member'].id}> find a chest and loot it.\r\n \
            <@{_players[0]['member'].id}> finds a {_weapons[0].name} and <@{_players[1]['member'].id}> finds a {_weapons[1].name}"

        else:
            _player = game.get_participant()
            _weapon = choice([y for _, y in WEAPON_LIST.items()], size=1, replace=False, p=WEAPON_WEIGHTS)[0]
            _player['weapon'] = _weapon
            _template = f"<@{_player['member'].id}> finds a chest and loots it. They find a {_weapon.name} inside."

        return ([], _template)


class Sponsor(Event):
    """Sponsor gives a chest and find a Weapon. Maybe items at some point"""
    def __init__(self):
        super().__init__("Loot", 1, False)

    def execute(self, game, players=None):
        if game.has_friendships():
            self.players = 2

        draw = random.randint(1, self.players)

        if draw == 2:
            _players = game.get_friendship_with_users()
            _weapons = choice([y for _, y in SPONSOR_LIST.items()], size=2, replace=False, p=SPONSOR_WEIGHTS)
            _players[0]['weapon'] = _weapons[0]
            _players[1]['weapon'] = _weapons[1]
            _template = f"A 3rd party sponsor has involved in a bet of very large amount of money and to make sure they don't lose, " \
                f"they have sponsored <@{_players[0]['member'].id}> and <@{_players[1]['member'].id}> with a chest.\r\n " \
                f"<@{_players[0]['member'].id}> gets a {_weapons[0].name} and <@{_players[1]['member'].id}> gets a {_weapons[1].name}!"

        else:
            _player = game.get_participant()
            _weapon = choice([y for _, y in SPONSOR_LIST.items()], size=1, replace=False, p=SPONSOR_WEIGHTS)[0]
            _player['weapon'] = _weapon
            _template = f"A 3rd party sponsor has involved in a bet of very large amount of money and to make sure they don't lose, " \
                f"they have sponsored <@{_player['member'].id}> with a chest.\r\n"  \
                f"They find a {_weapon.name} inside!"

        return ([], _template)


class Friendship(Event):
    def __init__(self):
        super().__init__("Friendship", 2, False)

    def execute(self, game, players=None):
        all_friendships = [user for friendship in game._friendships for user in friendship]
        _players = random.sample([user for user in game.participants if user not in all_friendships], self.players)

        # generate friendship
        game._friendships.append(_players)

        # generate template
        _template = f"<@{_players[0]['member'].id}> and <@{_players[1]['member'].id}> have decided to team up to have better chances to win."

        return (_players, _template)


class Betrayal(Event):
    def __init__(self):
        super().__init__("Betrayal", 2)

    def execute(self, game, players=None):
        if len(game._friendships) <= 0:
            _template = "There are no betrayals today."
            return ([], _template)

        _players = random.choice(game._friendships)

        # choose a loser
        _loser = random.choice(_players)
        _winner = _players[0] if _players[0] != _loser else _players[1]

        # generate template
        _template = f"<@{_winner['member'].id}> sees an opening and stabs <@{_loser['member'].id}> in the back."

        return ([_loser], _template)


class Romance(Event):
    EVENTS = [
        "<@{}> and <@{}> kiss each other under the moonlight.",
        "<@{}> and <@{}> lewdly hold their hands while walking.",
        "<@{}> and <@{}> share bed at night while wind blows their sheets.",
        "<@{}> and <@{}> promise to get married once everything is over.",
    ]

    def __init__(self):
        super().__init__("Romance", 2)

    def execute(self, game, players=None):
        _winners = game.get_friendship()
        if not _winners:
            return ([], "There were no Romances today.")

        # generate template
        return ([], random.choice(self.EVENTS).format(_winners[0]['member'].id, _winners[1]['member'].id))


class FinalRomance(Event):
    def __init__(self):
        super().__init__("FinalRomance", 2)

    def execute(self, game, players):
        # choose a loser
        _loser = random.choice(players)
        _winner = players[0] if players[0] != _loser else players[1]

        # generate template
        _template = f"<@{_winner['member'].id}> and <@{_loser['member'].id}> stare at each other in the middle of the arena."\
        + "The death bodies of their rivals all over the area, drenched in sweat, blood and tears they formed an alliance to get here,"\
        + "but now they realized that only one of them can win.\r\n"\
        + "They don't want to do it and put their weapons down, get close to each other and embrace in a loving hug. However "\
        + f"<@{_loser['member'].id}> feels a piercing pain in the back of their back and releases the hug, with an expression in their face "\
        + f"of fear and disbelief as they move their hand to their back to find <@{_winner['member'].id}>'s knife piercing their heart."\
        + "Slowly as their blood escapes from their body they get to their knees and finally fall off to the ground lifeless."

        return ([_loser], _template)



kill_events = [
    Kill(),
    Duel2(),
    Duel4(),
    Accident(),
]
kill_weights = [
    0.33,
    0.25,
    0.25,
    0.17,
]

low_kill_events = [
    Kill(),
    Duel2(),
    Accident(),
]
low_kill_weights = [
    0.45,
    0.45,
    0.10,
]

friend_events = [
    Friendship(),
    Betrayal(),
    Romance(),
]
friend_weights = [
    0.5,
    0.25,
    0.25
]

loot_events = [
    Loot(),
    Sponsor()
]
loot_weights = [
    0.7,
    0.3,
]