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
from exception import (
    ReplaceObjectException,
    NextLevelException,
    PreviousLevelException,
    CreateObject,
    AppendMessage)
from functools import partial
from room import Room, MagneticPathway
from constants import (
    MOVE_AROUND_MESSAGE,
    ATTACK_MESSAGE,
    SCROLL_MESSAGE,
    INTERACT_MESSAGE,
    HERO_ID)

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
    'closed shaft',
    id = 1
)

DESC_STAIRS = partial(
    Object,
    True,
    '>',
    'descending stairs',
    interact = descend_stairs,
    id = 2
)

def ascend_stairs(self):
    raise PreviousLevelException()

ASC_STAIRS = partial(
    Object,
    True,
    '<',
    'ascending stairs',
    interact = ascend_stairs,
    id = -2,
    x = 130,
    y = 90
)

leverid = 4

LEVER = partial(
    Object,
    go_through = True,
    symbol = 'L',
    description = 'lever',
    range = 5,
    interact = on_off_switch(
        partial(replace_object(1, DESC_STAIRS)),
        partial(replace_object(2, CLOSED_SHAFT))
    ),
    id = leverid
)

def append_message(msg):
    def fun(objects):
        raise AppendMessage(msg)
    return fun

BOULDER = partial(
    Object,
    go_through = False,
    symbol = 'O',
    description = 'large boulder blocking the stairs',
    x = 130,
    y = 90,
    range = 5,
    interact=append_message("It won't budge")
)

BASE_CHEST = partial(
    Object,
    go_through = True,
    symbol = 'C',
    range = 5
)

def debug(self):
    print 'hello'

TREASURE_CHEST = partial(
    BASE_CHEST,
    description = 'treasure chest',
    interact = debug,
    x = 100,
    y = 100
)

wolfid = 3

WOLF = partial(
    Creature,
    symbol = 'W',
    description = 'dire wolf',
    health=1,
    speed=2,
    strength=5,
    light_radius=20,
    range=10,
    attack_type=MeleeHitbox,
    id=wolfid,
    interaction=append_message('This wolf is too busy trying to kill you')
)

def create_boulder(objects):
    raise ReplaceObjectException(-2, BOULDER)

BLOCK_STAIRS_TRIGGER = RunOnceTrigger(
    create_boulder,
    HeroEnterRegion(144, 100, 10, 10),
    [])

TUTORIAL1 = RunOnceTrigger(
    append_message(MOVE_AROUND_MESSAGE),
    HeroEnterRegion(144, 100, 10, 10),
    [])

TUTORIAL2 = RunOnceTrigger(
    append_message(ATTACK_MESSAGE),
    HeroEnterRegion(50, 160, 100, 10),
    [])

def scroll_message_pred(objects):
    return any(o.dead() for o in objects)

def scroll_message_fun(objects):
    raise AppendMessage(SCROLL_MESSAGE)

TUTORIAL3 = RunOnceTrigger(
    scroll_message_fun,
    Predicate([wolfid], scroll_message_pred),
    [])

def interact_message_pred(objects):
    return objects[0].visible(objects[1])

def interact_message_fun(objects):
    raise AppendMessage(INTERACT_MESSAGE)

TUTORIAL4 = RunOnceTrigger(
    interact_message_fun,
    Predicate([HERO_ID, leverid], interact_message_pred),
    [])

room1 = Room(50, 50, 100, 100,
             objects=[CLOSED_SHAFT],
             start=True)

room2 = Room(300, 200, 100, 150,
             creatures=[(WOLF, 2)],
             objects=[LEVER])

room3 = Room(50, 220, 100, 100,
             creatures=[WOLF])

p1 = MagneticPathway(room1, room3)
p2 = MagneticPathway(room2, room3)

L1 = partial(
    Level,
    objects = [TREASURE_CHEST, ASC_STAIRS],
    rooms = [
        room1,
        room2,
        room3
    ],
    pathways = [p1, p2],
    creatures = [],
    triggers = [
        BLOCK_STAIRS_TRIGGER,
        TUTORIAL1,
        TUTORIAL2,
        TUTORIAL3,
        TUTORIAL4]
)

LEVELS = [
    L1
]
