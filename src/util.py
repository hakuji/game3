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

"""Helper classes"""

import pyglet
from pyglet.window import key
from constants import (FIELD_FONT_SIZE as FONT_SIZE, OBJECT_FONT_SIZE,
                       ST_BOUND_Y, ST_BOUND_X, OBJECT_FONT_FACE)
import itertools
from random import randint as random
flatten = itertools.chain.from_iterable

class SubscriptionFound(Exception):
    pass

class KeySubscription(object):
    """Keyboard inputs combination that trigger an event"""
    def __init__(self, action, key, modifiers=0):
        self.key = key
        self.modifiers = modifiers
        self.action = action
    def __str__(self):
        return key.symbol_string(self.key) + ' ' + key.modifiers_string(self.modifiers)
    def react(self, key, modifiers):
        if self.key == key and self.modifiers == modifiers:
            self.action()
            raise SubscriptionFound()

class Drawable(object):
    """Anything that can be drawn"""
    def __init__(self, sprite):
        self.sprite = sprite
    def draw(self):
        self.sprite.draw()

class Container(object):
    def __init__(self, contents):
        self.contents = contents
    def draw(self):
        for i in self.contents:
            i.draw()

class Reactable(object):
    """Anything that can react to keyboard inputs"""
    def __init__(self, subs):
        self.subs = subs
    def react(self, key, modifiers):
        for i in self.subs:
            i.react(key, modifiers)

class Option(Drawable, Reactable):
    """Option accessed with a key"""
    def __init__(self, subs, description, sprite):
        self.subs = subs
        self.description = description
        self.sprite = sprite
        self.sprite.text = self.get_text()
    def keypart(self):
        keystr = [str(i) for i in self.subs]
        if len(keystr) > 1:
            return ', '.join(keystr[:-1]) + ' or ' + keystr[-1]
        else:
            return keystr[0]
    def get_text(self):
        return self.keypart() + ' - ' + self.description

class Screen(Container):
    def react(self, key, modifiers):
        for i in self.contents:
            try:
                i.react(key, modifiers)
            except AttributeError:
                pass

class ObjectDefinition(object):
    """The common properties of a type of object"""
    def __init__(self, id, go_through, symbol, description):
        self.id = id
        self.go_through = go_through
        self.symbol = symbol
        self.description = description
    def toScreen(self, count):
        return [Object(self) for i in range(count)]

class CreatureDefinition(ObjectDefinition):
    """The common properties of a creature"""
    def __init__(self, id, symbol, description, health, speed, strength,
                 stationary = False, hostile = True, go_through = False):
        super(CreatureDefinition, self).__init__(id, go_through, symbol, description)
        self.health = health
        self.speed = speed
        self.hostile = hostile
        self.stationary = stationary
    def toScreen(self, count):
        return [Creature(self) for i in range(count)]

class Object(Drawable):
    """Actual object on the screen"""
    @classmethod
    def from_list(cls, l):
        return list(flatten(map(lambda x: x[0].toScreen(x[1]), l)))
    def __init__(self, definition):
        sprite = pyglet.text.Label(
            definition.symbol,
            font_name=OBJECT_FONT_FACE,
            font_size=OBJECT_FONT_SIZE)
        super(Object, self).__init__(sprite)
        self.definition = definition
    def contains(self, x, y, height, width):
        """Used to detect collision"""
        return False

class Creature(Object):
    """Actual creature on the screen"""
    def __init__(self, definition):
        super(Creature, self).__init__(definition)
    def update(self, dt):
        if self.definition.stationary:
            pass
        else:
            if self.definition.hostile:
                if self.within_range():
                    self.attack()
                else:
                    self.chase()
            else:
                self.roam()
    def within_range(self):
        return False
    def attack(self):
        pass
    def chase(self):
        print 'Here'

class Hero(Object):
    def __init__(self, khandler, lvl = 0, inv = None):
        d = ObjectDefinition(2, False, '@', 'You, the traveler')
        super(Hero, self).__init__(d)
        self.lvl = lvl
        self.inv = inv
        self.khandler = khandler
        self.speed = 3
        if inv is None:
            self.inv = []
    def update(self, dt):
        if self.khandler[key.UP]:
            self.sprite.y += self.speed
        if self.khandler[key.DOWN]:
            self.sprite.y -= self.speed
        if self.khandler[key.LEFT]:
            self.sprite.x -= self.speed
        if self.khandler[key.RIGHT]:
            self.sprite.x += self.speed

class StageDefinition(object):
    def __init__(self, obj_definitions, room_definitions,
                 creature_definitions):
        self.obj_definitions = obj_definitions
        self.room_definitions = room_definitions
        self.creature_definitions = creature_definitions

class Stage(Container):
    def __init__(self, stage_def, hero):
        self.rooms = stage_def.room_definitions
        self.objects = Object.from_list(stage_def.obj_definitions)
        self.creatures = Creature.from_list(stage_def.creature_definitions)
        self.creatures.append(hero)
        self.contents = []
        self.contents.extend(self.rooms)
        self.contents.extend(self.objects)
        self.contents.extend(self.creatures)
        super(Stage, self).__init__(self.contents)
        self.arrange_objects()
    def placeable_objects(self):
        return itertools.chain(self.objects, self.creatures)
    def arrange_objects(self):
        """Set initial arrangement of the objects"""
        for obj in self.placeable_objects():
            self.set_location(obj)
    def get_random_position(self, width, height):
        """Returns a random point in the map"""
        x = random(0, ST_BOUND_X - width)
        y = random(0, ST_BOUND_Y - height)
        return x, y
    def set_location(self, obj):
        """Assign a random free position to an object. Will try 10000 times
before raising an exception"""
        width = obj.sprite.content_width
        height = obj.sprite.content_height
        if obj.definition.go_through:
            x, y = self.get_random_position(width, height)
            obj.sprite.x = x
            obj.sprite.y = y
            return
        for i in range(10000):
            x, y = self.get_random_position(width, height)
            if not any(i.contains(x, y, width, height)
                       for i in self.placeable_objects()):
                obj.sprite.x = x
                obj.sprite.y = y
                return
        raise Exception('Could not assign a position to object: '
                        + str(obj))


class LabeledField(Container):
    def __init__(self, label, value_func, x, y):
        self.label = pyglet.text.Label(
            label + ':',
            font_name='Times',
            font_size=FONT_SIZE,
            x=x, y=y)
        self.value = pyglet.text.Label(
            font_name='Times',
            font_size=FONT_SIZE,
            x = x + self.label.content_width + 15,
            y = y)
        self.value_func = value_func
        self.contents = [self.label, self.value]

    def draw(self):
        self.value.text = str(self.value_func())
        super(LabeledField, self).draw()
