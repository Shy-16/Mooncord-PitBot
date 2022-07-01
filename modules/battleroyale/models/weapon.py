# -*- coding: utf-8 -*-

## Weapon Class ##
# Holds a bit of information to parse during BR events #

from functools import total_ordering

from .event import Arena


@total_ordering
class Weapon:

    def __init__(self, name, power, w_range) -> None:
        self._name = name
        self._power = power
        self._range = w_range

    def __eq__(self, other) -> bool:
        return self._power == other._power

    def __gt__(self, other) -> bool:
        if self._range > other._range:
            return True
        elif self._range < other._range:
            return False
        return self._power > other._power

    @property
    def name(self):
        return self._name

    @property
    def power(self):
        return self._power

    @property
    def range(self):
        return self._range

    def arena(self, arena: str) -> str:
        """
        Returns a string in base to the arena
        """
        return ""

    def use(self) -> str:
        """
        Returns a string to print in BR events
        """
        return ""

    def death(self, killed: dict) -> str:
        """
        Returns a string describing the death
        """
        return ""


class ShortBlunt(Weapon):
    def __init__(self, name, power) -> None:
        super().__init__(name, power, 1)

    def use(self) -> str:
        return f" grips the handle of their {self._name} and swings it smashing "


class LongBlunt(Weapon):
    def __init__(self, name, power) -> None:
        super().__init__(name, power, 2)

    def use(self) -> str:
        return f" grips the handle of their {self._name} and swings it smashing "


class ShortBlade(Weapon):
    def __init__(self, name, power) -> None:
        super().__init__(name, power, 1)

    def use(self) -> str:
        return f" grips the handle of their {self._name} and slashes it cutting "


class LongBlade(Weapon):
    def __init__(self, name, power) -> None:
        super().__init__(name, power, 2)

    def use(self) -> str:
        return f" grips the handle of their {self._name} and swings it cutting "


class Pistol(Weapon):
    def __init__(self, name, power) -> None:
        super().__init__(name, power, 3)

    def use(self) -> str:
        return f" grips the handle of their {self._name} and pulls the trigger shooting "


class Rifle(Weapon):
    def __init__(self, name, power) -> None:
        super().__init__(name, power, 5)

    def arena(self, arena: str) -> str:
        _template = ""

        if arena == Arena.OPEN_FIELD:
            _template = f"drops on their knee and aims their {self._name}"

        elif arena == Arena.FOREST:
            _template = f"hides in a bush and skillfully aims their {self._name}"

        elif arena == Arena.TUNNEL:
            _template = f"hides behind some rubble and peeks aiming their {self._name}"

        elif arena == Arena.HOUSE:
            _template = f"aims towards a window from the outside aiming their {self._name}"

        elif arena == Arena.TOWER:
            _template = f"goes to the top and looks for a prey below aiming their {self._name}"

        return _template

    def use(self) -> str:
        return "shooting"

    def death(self, killed: dict) -> str:
        return f"going straight through <@{killed['user_id']}>'s head splashing their brains all over the floor."


WEAPON_LIST = {
    'knuckles': ShortBlunt('Knuckles', 1),
    'baseball_bat': LongBlunt('Baseball Bat', 1),
    'knife': ShortBlade('Knife', 1),
    'military_knife': ShortBlade('Military Knife', 2),
    'machete': LongBlade('Machete', 2),
    'katana': LongBlade('Katana', 3),
    'revolver': Pistol('Revolver', 3),
    'deagle': Pistol('Desert Eagle', 4),
    'shotgun': Rifle('Shotgun', 4),
    'ar14': Rifle('AR-14', 5),
    'sniper': Rifle('Sniper Rifle', 8)
}

WEAPON_WEIGHTS = [
    0.12,
    0.12,
    0.12,
    0.12,
    0.12,
    0.08,
    0.08,
    0.08,
    0.06,
    0.05,
    0.05
]

if __name__ == '__main__':
    sbt = WEAPON_LIST['knuckles']
    lbt = WEAPON_LIST['baseball_bat']
    sbl = WEAPON_LIST['knife']
    lbl = WEAPON_LIST['katana']
    spt = WEAPON_LIST['deagle']
    lpt = WEAPON_LIST['sniper']

    print(sbt > lbt)
    print(lbt > sbt)
    print(lbt > sbl)
    print(sbl > lbt)
    print(lpt > lbl)
    print(sbt > spt)

    from numpy.random import choice

    for i in range(10):
        print(choice(list(WEAPON_LIST.keys()), size=1, replace=False, p=WEAPON_WEIGHTS))
