# Copyright 2013 by akuji
#
# This file is part of game 3.
#
# game 3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# game 3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with game 3.  If not, see <http://www.gnu.org/licenses/>.

from util import (Object, CreatureDefinition, Level,
                  Room, NextLevelException, MagneticPathway,
                  ReplaceObjectException)
from functools import partial

def descend_stairs(self):
    raise NextLevelException()

def replace_object(this, that):
    """Replace this with that"""
    def r(self):
        raise ReplaceObjectException(this, that)
    return r

def on_off_switch(f1, f2):
    """Will call f1 if the switch set otherwise f2"""
    def fun(self):
        if getattr(self, 'on', False):
            self.on = False
            f2(self)
        else:
            self.on = True
            f1(self)
    return fun

CLOSED_SHAFT = partial(
    Object,
    True,
    '|',
    'Closed shaft',
    id = 1
)

DESC_STAIRS = partial(
    Object,
    True,
    '>',
    'Descending stairs',
    interact = descend_stairs,
    id = 2
)

LEVER = partial(
    Object,
    go_through = True,
    symbol = 'L',
    description = 'A lever',
    range = 5,
    interact = on_off_switch(
        partial(replace_object(1, DESC_STAIRS)),
        partial(replace_object(2, CLOSED_SHAFT)))
)

BASE_CHEST = partial(
    Object,
    go_through = True,
    symbol = 'C',
    range = 5
)

DECORATIVE_CHEST = partial(
    BASE_CHEST,
    description = 'A decorative chest'
)

def debug(self):
    print 'hello'

TREASURE_CHEST = partial(
    BASE_CHEST,
    description = 'A treasure chest',
    interact = debug
)

WOLF = CreatureDefinition(
    symbol = 'W',
    description = 'Wolf',
    health=10,
    speed=2,
    strength=0,
    light_radius=20,
    range=10)

room1 = Room(50, 50, 100, 100,
             object_def=[CLOSED_SHAFT],
             start=True)

room2 = Room(300, 200, 100, 150,
             creature_def=[(WOLF, 2)],
             object_def=[LEVER])
room3 = Room(50, 220, 100, 100,
             object_def=[DECORATIVE_CHEST,
                         TREASURE_CHEST])

p1 = MagneticPathway(room1, room3)
p2 = MagneticPathway(room2, room3)

L1 = partial(Level,
    objects = [],
    rooms = [
        room1,
        room2,
        room3
    ],
    pathways = [p1, p2],
    creature_definitions = []
)

LEVELS = [
    L1
]
