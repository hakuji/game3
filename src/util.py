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

import pyglet, itertools
from pyglet.window import key
from constants import Direction, HERO_ID
from rect import Rect
from decorations import autoset
from exception import (
    SubscriptionFound,
    AnimationEnd)
from function import vertex_list_from_rect

flatten = itertools.chain.from_iterable

class KeySubscription(object):
    """Keyboard inputs combination that trigger an event"""
    @autoset
    def __init__(self, action, key, modifiers=0):
        pass
    def __str__(self):
        return key.symbol_string(self.key) + ' ' + key.modifiers_string(self.modifiers)
    def react(self, key, modifiers):
        if self.key == key and self.modifiers == modifiers:
            self.action()
            raise SubscriptionFound()

class Drawable(object):
    """Anything that can be drawn"""
    @autoset
    def __init__(self, sprite):
        pass
    def draw(self):
        self.sprite.draw()

class Container(object):
    @autoset
    def __init__(self, contents):
        pass
    def update(self):
        pass
    def draw(self):
        for i in self.contents:
            i.draw()

class Reactable(object):
    """Anything that can react to keyboard inputs"""
    @autoset
    def __init__(self, subs):
        pass
    def react(self, key, modifiers):
        for i in self.subs:
            i.react(key, modifiers)

class Hitbox(Drawable):
    @autoset
    def __init__(self, origin, x, y, w, h):
        self.strength = origin.strength
        self.remove = False
        self.sprite = vertex_list_from_rect(x, y, w, h)
        self.rect = Rect.from_dimensions(x, y, w, h)
    def hit(self, creature):
        return self.rect.overlaps(creature.rect)
    def draw(self):
        self.sprite.draw(pyglet.gl.GL_QUAD_STRIP)

class MeleeHitbox(Hitbox):
    def __init__(self, origin,  x, y, w, h):
        super(MeleeHitbox, self).__init__(
            origin, x, y, w, h)
    def hit(self, creature):
        if creature == self.origin:
            return False
        else:
            return super(MeleeHitbox, self).hit(creature)

class Animation(object):
    """Some kind of object animation"""
    def __init__(self):
        pass

class Move(Animation):
    @autoset
    def __init__(self, direction, distance, obj):
        self.destination_set = False
        self.pos = None
    def final_destination(self):
        x, y = self.obj.x, self.obj.y
        if self.direction[0] == Direction.EAST:
            x += self.distance
        elif self.direction[0] == Direction.WEST:
            x -= self.distance
        if self.direction[1] == Direction.NORTH:
            y += self.distance
        elif self.direction[1] == Direction.SOUTH:
            y -= self.distance
        return x, y
    def update(self):
        if not self.destination_set:
            self.pos = self.final_destination()
            self.destination_set = True
        else:
            self.obj.move_towards(self.pos[0], self.pos[1])
        if self.pos[0] == self.obj.x and self.pos[1] == self.obj.y:
            raise AnimationEnd()

class ObjectMessage(object):
    @autoset
    def __init__(self, message, obj):
        pass
    def __str__(self):
        return self.message.format(self.obj.description, self.obj.symbol)
    def index(self):
        """Where to start formating"""
        return str(self).index(self.obj.symbol)

class RunOnceTrigger(object):
    """A trigger that once the predicate evaluate true, cause a reaction on objects"""
    @autoset
    def __init__(self, reaction, predicate, object_ids):
        self.used = False
        self.trigger_objs = None
    def set_objects(self, predicate_objs, trigger_objs):
        self.predicate.objects = predicate_objs
        self.objects = trigger_objs
    def update(self):
        if not self.used:
            if self.predicate.eval():
                self.used = True
                self.reaction(self.objects)

class Predicate(object):
    """A condition of a trigger"""
    @autoset
    def __init__(self, object_ids, fun):
        pass
    def eval(self):
        return self.fun(self.objects)

class HeroEnterRegion(Predicate):
    """A predicate that evaluates true if the hero is inside a region"""
    def __init__(self, x, y, w, h):
        rect = Rect.from_dimensions(x, y, w, h)
        def fun(objects):
            return rect.overlaps(objects[0].rect)
        super(HeroEnterRegion, self).__init__([HERO_ID], fun)
