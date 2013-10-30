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

from util import MeleeHitbox, RunOnceTrigger, HeroEnterRegion, Predicate
from obj import Object
from creature import Creature
from level import Level
from function import raise_ev, once
from exception import (
    ReplaceObject,
    NextLevel,
    PreviousLevel,
    EventList,
    AppendMessage,
    AddPathway)
from functools import partial
from room import Room, MagneticPathway
from constants import (
    MOVE_AROUND_MESSAGE,
    ATTACK_MESSAGE,
    SCROLL_MESSAGE,
    INTERACT_MESSAGE,
    HERO_ID,
    Color)

CLOSED_SHAFT = partial(
    Object,
    True,
    '|',
    'closed shaft',
    id = 1,
    color = Color.BATTLESHIPGREY
)

DESC_STAIRS = partial(
    Object,
    True,
    '>',
    'descending stairs',
    interact = raise_ev(NextLevel),
    id = 2
)

ASC_STAIRS = partial(
    Object,
    True,
    '<',
    'ascending stairs',
    interact = raise_ev(PreviousLevel),
    id = -2,
    x = 130,
    y = 90
)

leverid = 4

def replace_for_lever(this, that):
    def r(self):
        msg_ev = AppendMessage('You hear a rumbling noise form southeast')
        raise EventList([ReplaceObject(this, that), msg_ev])
    return r

append_message = partial(raise_ev, AppendMessage)

BOULDER = partial(
    Object,
    go_through = False,
    symbol = 'O',
    description = 'large boulder blocking the stairs',
    x = 130,
    y = 90,
    range = 5,
    interact=append_message("You will deal with this later"),
    color=Color.UMBER
)

BASE_CHEST = partial(
    Object,
    go_through = True,
    symbol = 'C',
    range = 5,
    color=Color.BURLYWOOD
)

TREASURE_CHEST = partial(
    BASE_CHEST,
    description = 'treasure chest',
    interact = append_message("It's empty"),
    x = 100,
    y = 100
)

wolfid = 3

WOLF = partial(
    Creature,
    symbol = 'W',
    description = 'guardian wolf',
    health=1000,
    speed=2,
    strength=500,
    light_radius=60,
    range=10,
    attack_type=MeleeHitbox,
    id=wolfid,
    interaction=append_message('This wolf is too busy trying to kill you'),
    color=Color.GOLD
)

HOLY_SWORDSMAN = partial(
    Creature,
    symbol = 'H',
    description = 'holy swordsman',
    health=4000,
    speed=2,
    strength=2000,
    light_radius=30,
    range=10,
    attack_type=MeleeHitbox,
    interaction=append_message('Swordsman: Die monster!'),
    color=Color.WHITE
)

SWORDSMAN_TRIGGER = RunOnceTrigger(
    raise_ev(AppendMessage, '?????: Do not let that demon reach the next level!'),
    HeroEnterRegion(360, 190, 100, 10),
    [])

BLOCK_STAIRS_TRIGGER = RunOnceTrigger(
    raise_ev(ReplaceObject, -2, BOULDER),
    HeroEnterRegion(144, 100, 10, 10),
    [])

TUTORIAL1 = RunOnceTrigger(
    append_message(MOVE_AROUND_MESSAGE),
    HeroEnterRegion(144, 100, 10, 10),
    [])

TUTORIAL2 = RunOnceTrigger(
    append_message(ATTACK_MESSAGE),
    HeroEnterRegion(50, 200, 100, 10),
    [])

def scroll_message_pred(objects):
    return any(o.dead() for o in objects)

TUTORIAL3 = RunOnceTrigger(
    raise_ev(AppendMessage, SCROLL_MESSAGE),
    Predicate([wolfid], scroll_message_pred),
    [])

def interact_message_pred(objects):
    return objects[0].visible(objects[1])


TUTORIAL4 = RunOnceTrigger(
    raise_ev(AppendMessage, INTERACT_MESSAGE),
    Predicate([HERO_ID, leverid], interact_message_pred),
    [])

room1 = Room(50, 50, 100, 100,
             start=True)

room2 = Room(300, 200, 100, 150,
             creatures=[(WOLF, 6)],
             objects=[])

room3 = Room(50, 220, 100, 100,
             creatures=[WOLF])

room4 = Room(335, 90, 40, 27,
             objects=[DESC_STAIRS],
             creatures=[(HOLY_SWORDSMAN, 3)])

p1 = MagneticPathway(room1, room3)
p2 = MagneticPathway(room2, room3)
p3 = MagneticPathway(room2, room4)

LEVER = partial(
    Object,
    go_through = True,
    symbol = 'L',
    description = 'lever',
    range = 5,
    interact = once(raise_ev(
        EventList,
        AddPathway(p3),
        AppendMessage('A secret door opens')
    )),
    id = leverid,
    color=Color.BATTLESHIPGREY,
    x=389,
    y=210
)

L1 = partial(
    Level,
    objects = [TREASURE_CHEST, ASC_STAIRS, LEVER],
    rooms = [
        room1,
        room2,
        room3,
        room4
    ],
    pathways = [p1, p2],
    creatures = [],
    triggers = [
        BLOCK_STAIRS_TRIGGER,
        TUTORIAL1,
        TUTORIAL2,
        TUTORIAL3,
        TUTORIAL4,
        SWORDSMAN_TRIGGER]
)

LEVELS = [
    L1
]
