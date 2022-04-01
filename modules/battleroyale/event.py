# -*- coding: utf-8 -*-

## Event Class ##
# Covers functionality for events during BR #

import random

class Event:

	def __init__(self, name, players=4, has_losers=True):

		self.name = name
		self.players = players
		self.has_losers = has_losers

	def execute(self, br_module):
		"""
		Execute the event
		"""
		pass


class Duel2(Event):

	def __init__(self):
		super().__init__("Duel", 2)

	def execute(self, br_module, players=None):

		# choose 2 players
		if players:
			_players = self._players
		else:
			_players = random.choices(br_module.participants, k=self.players)

		# choose a loser
		_loser = random.choice(_players)

		# format template
		_template = f"<@{_players[0]}> and <@{_players[1]}> cross each other in the battlefield.\r\n \
		<@{_loser}> gets mercilessly stabbed in the heart to death."

		return ([_loser], _template)

class Duel4(Event):

	def __init__(self):
		super().__init__("Duel", 4)

	def execute(self, br_module, players=None):

		# choose 4 players
		if players:
			_players = self._players
		else:
			_players = random.choices(br_module.participants, k=self.players)

		# choose how many losers there are
		total_losers = random.randint(1, self.players-1)

		# get losers
		_losers = random.choices(_players, k=total_losers)
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

	def execute(self, br_module):

		# choose 2 players
		all_friendships = [user for friendship in br_module._friendships for user in friendship]
		_players = random.choices([user for user in br_module.participants if user not in all_friendships], k=self.players)

		# generate friendship
		br_module._friendships.append(_players)

		# generate template
		_template = f"<@{_players[0]}> and <@{_players[1]}> have decided to team up to have better chances to win."

		return (_players, _template)

class Betrayal(Event):

	def __init__(self):
		super().__init__("Friendship", 2)

	def execute(self, br_module):

		# choose 2 players
		_players = random.choice(br_module._friendships)

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

