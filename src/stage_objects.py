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

from util import (ObjectDefinition, CreatureDefinition, StageDefinition,
                  Room, NextLevelException, MagneticPathway,
                  ReplaceObjectException)

def descend_stairs(self):
    raise NextLevelException()

def replace_object(this, that):
    """Replace this with that"""
    def r(self):
        raise ReplaceObjectException(this, that)
    return r

CLOSED_SHAFT = ObjectDefinition(-2, True, '|', 'Closed shaft')

DESC_STAIRS = ObjectDefinition(1, True, '>', 'Descending stairs',
                               interaction = descend_stairs)

LEVER = ObjectDefinition(
    id = 2,
    go_through = True,
    symbol = 'L',
    description = 'A lever',
    range = 5,
    interaction = replace_object(CLOSED_SHAFT, DESC_STAIRS)
)

WOLF = CreatureDefinition(
    id = 2,
    symbol = 'W',
    description = 'Wolf',
    health=10,
    speed=2,
    strength=20,
    light_radius=20,
    range=10)

room1 = Room(50, 50, 100, 100,
             object_def=[(CLOSED_SHAFT, 1)],
             start=True)

room2 = Room(300, 200, 100, 150,
             creature_def=[(WOLF, 2)],
             object_def=[(LEVER, 1)])
room3 = Room(50, 220, 100, 100)

p1 = MagneticPathway(room1, room3)
p2 = MagneticPathway(room2, room3)

ST1 = StageDefinition(
    obj_definitions = [],
    rooms = [
        room1,
        room2,
        room3
    ],
    pathways = [p1, p2],
    creature_definitions = [],
)

STAGES = [
    ST1
]
