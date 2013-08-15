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
from constants import FIELD_FONT_SIZE as FONT_SIZE, OBJECT_FONT_SIZE, ST_BOUND_Y, ST_BOUND_X
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

class Hero(Drawable):
    def __init__(self, khandler, lvl = 0, inv = None):
        self.sprite = pyglet.text.Label(
            '@',
            font_name='Monospace',
            font_size=12)
        self.lvl = inv
        self.khandler = khandler
        if inv is None:
            self.inv = []
    def update(self):
        pass
    def move_left(self):
        self.sprite.x = max(1, self.sprite.x - 1) #TODO: Real boundary check

    def move_right(self):
        self.sprite.x = self.sprite.x + 1

class ObjectDefinition(object):
    """The common properties of a type of object"""
    def __init__(self, id, go_through, symbol, description):
        self.id = id
        self.go_through = go_through
        self.symbol = symbol
        self.description = description
    def toScreenObject(self, count):
        return [Object(self) for i in range(count)]

class Object(Drawable):
    """Actual object on the screen"""
    @classmethod
    def from_list(cls, l):
        return list(flatten(map(lambda x: x[0].toScreenObject(x[1]), l)))
    def __init__(self, definition):
        sprite = pyglet.text.Label(
            definition.symbol,
            font_name='Monospace',
            font_size=OBJECT_FONT_SIZE)
        super(Object, self).__init__(sprite)
        self.definition = definition
    def contains(self, x, y, height, width):
        """Used to detect collision"""
        return False

class Stage(Container):
    def __init__(self, object_list, walls, creatures):
        self.walls = walls
        self.objects = Object.from_list(object_list)
        self.creatures = creatures
        self.contents = []
        self.contents.extend(walls)
        self.contents.extend(self.objects)
        self.contents.extend(creatures)
        super(Stage, self).__init__(self.contents)
        self.arrange_objects()
    def arrange_objects(self):
        """Set initial arrangement of the objects"""
        for obj in self.objects:
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
                       for i in self.objects):
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
