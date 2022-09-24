# -*- coding: utf-8 -*-

## Arena Class ##
# Covers functionality for events during BR #

import random

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
