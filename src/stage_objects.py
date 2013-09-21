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
                  Room, NextLevelException, Pathway, MagneticPathway)

def descend_stairs(self):
    raise NextLevelException()

DESC_STAIRS = ObjectDefinition(1, True, '>', 'Descending stairs',
                               interaction = descend_stairs)
PROP = ObjectDefinition(
    id = 2,
    go_through = False,
    symbol = 'P',
    description = 'A test prop',
    range = 20)

WOLF = CreatureDefinition(
    id = 2,
    symbol = 'W',
    description = 'Wolf',
    health=10,
    speed=2,
    strength=1,
    light_radius=20,
    range=10)

room1 = Room(50, 50, 100, 100,
             obj_def=[(DESC_STAIRS, 1)],
             start=True)

room2 = Room(300, 200, 100, 150,
             creat_def=[(WOLF, 2)],
             obj_def=[(PROP, 1)])
room3 = Room(50, 220, 100, 100)

p1 = MagneticPathway(room1, room3)
p2 = MagneticPathway(room2, room3)

ST1 = StageDefinition(
    obj_definitions = [],
    room_definitions = [
        room1,
        room2,
        room3
    ],
    pathway_definitions = [p1, p2],
    creature_definitions = [],
)

STAGES = [
    ST1
]
