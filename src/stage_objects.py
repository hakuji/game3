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
                  RoomDefinition)

DESC_STAIRS = ObjectDefinition(1, True, '>', 'Descending stairs')

WOLF = CreatureDefinition(2, 'W', 'Wolf', 10, 1, 1)

ST1 = StageDefinition(
    obj_definitions = [(DESC_STAIRS, 1)],
    room_definitions = [RoomDefinition(100, 100)],
    creature_definitions = [(WOLF, 2)],
    random_room_no = 2)

STAGES = [
    ST1
]
