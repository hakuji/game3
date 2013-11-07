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

from functools import partial
from level import Level
from room import Room, MagneticPathway
from level_util import ASC_STAIRS

r1 = Room(335, 54, 65, 119, start=True)
r2 = Room(192, 58, 52, 37)
r3 = Room(53, 142, 61, 42)
r4 = Room(65, 24, 56, 38)
r5 = Room(468, 96, 57, 42)
r6 = Room(344, 302, 62, 49)
r7 = Room(512, 310, 49, 46)
r8 = Room(198, 241, 52, 115)
r9 = Room(51, 325, 71, 36)
r10 = Room(51, 251, 83, 28)
r11 = Room(510, 213, 54, 42)
r12 = Room(304, 234, 29, 32)

p1 = MagneticPathway(r1, r2)
p2 = MagneticPathway(r1, r3)
p3 = MagneticPathway(r4, r3)
p4 = MagneticPathway(r1, r5)
p5 = MagneticPathway(r1, r6)
p6 = MagneticPathway(r6, r7)
p7 = MagneticPathway(r6, r8)
p8 = MagneticPathway(r8, r9)
p9 = MagneticPathway(r9, r10)
p10 = MagneticPathway(r7, r11)
p11 = MagneticPathway(r8, r12)

LEVEL = partial(
    Level,
    objects=[ASC_STAIRS],
    rooms=[r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12],
    pathways=[p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11],
    creatures=[],
    triggers=[]
)
