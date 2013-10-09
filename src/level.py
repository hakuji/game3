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

import itertools
from random import randint
from exception import ReplaceObjectException, CreatureDeathException
from util import Container, Object
from rect import Rect

rect1 = Rect.from_dimensions(0, 0, 0, 0)
rect2 = Rect.from_dimensions(0, 0, 0, 0)

class Level(Container):
    """A game level, stage etc"""
    def __init__(self, hero, objects, rooms, pathways,
                 creatures):
        self.pathways = pathways
        self.rooms = rooms
        self.objects = Object.from_list(objects)
        self.creatures = Object.from_list(creatures)
        self.arrange_objects()
        self.hero = hero
        self.init_rooms()
        self.set_enemies()
        self.contents = []
        self.hitboxes = []
        self.contents.append(self.rooms)
        self.contents.append(self.pathways)
        self.contents.append(self.objects)
        self.contents.append(self.hitboxes)
        self.contents.append(self.creatures)
        super(Level, self).__init__(self.contents)
    def init_rooms(self):
        for r in self.rooms:
            if r.start:
                self.set_location(self.hero, r)
                self.creatures.append(self.hero)
            creatures = Object.from_list(r.creatures)
            for c in creatures:
                self.creatures.append(c)
                self.set_location(c, r)
            objects = Object.from_list(r.objects)
            for o in objects:
                self.objects.append(o)
                self.set_location(o, r)
    def set_enemies(self):
        for i in self.creatures:
            if getattr(i, 'hostile', False):
                i.target = self.hero
    def remove_object(self, obj):
        self.objects.remove(obj)
    def add_object(self, obj, x, y):
        """Add and place an object"""
        self.objects.append(obj)
        obj.set_location(x, y)
    def replace_object(self, ex):
        """Use a replace exception to replace an object, if the object
does not exist. Fail silently"""
        this = filter(lambda o: o.id == ex.this, self.objects)
        if len(this) > 0:
            this = this[0]
        else:
            return
        self.remove_object(this)
        self.add_object(ex.that(), this.x, this.y)
    def update(self):
        del self.hitboxes[:]
        for obj in self.objects:
            obj.update()
        self.update_creatures()
        self.update_hitboxes()
        try:
            self.hero_interact()
        except ReplaceObjectException as ex:
            self.replace_object(ex)
    def update_creatures(self):
        for c in self.creatures[:]:
            try:
                c.update()
                self.update_position(c)
                self.add_hitbox(c)
            except CreatureDeathException:
                self.creatures.remove(c)
    def add_hitbox(self, creature):
        if creature.hitbox is not None:
            self.hitboxes.append(creature.hitbox)
            creature.hitbox = None
    def update_hitboxes(self):
        for b in self.hitboxes:
            self.hitbox_eval(b)
    def hitbox_eval(self, b):
        for c in self.creatures:
            if b.hit(c):
                c.be_attacked(b)
    def hero_interact(self):
        if self.hero.intended_interact:
            for o in self.placeable_objects():
                if o == self.hero:
                    continue
                if o.within_range(self.hero):
                    o.interact()
                    return
    def update_position(self, creature):
        if not creature.go_through:
            w = creature.w
            h = creature.h
            for i in creature.movements():
                if (self.contained_in_any_room(i[0], i[1], w, h)
                    and not self.collide_with_objects(i[0], i[1], w, h, creature)):
                    creature.x = i[0]
                    creature.y = i[1]
                    break
                else:
                    pass
    def placeable_objects(self):
        return itertools.chain(self.objects, self.creatures)
    def arrange_objects(self):
        """Set initial arrangement of the objects"""
        for obj in self.placeable_objects():
            if obj.x == 0 and obj.y == 0:
                self.set_location(obj)
    def get_random_position_in_room(self, width, height, room):
        """Returns a random walkable point in a room"""
        rect = room.inner_rect
        x = randint(rect.left, rect.right)
        y = randint(rect.bottom, rect.top)
        return x, y
    def get_random_position(self, width, height):
        """Returns a random walkable point in the map"""
        lc = list(self.get_containing_places())
        room = lc[randint(0, len(lc) - 1)]
        return self.get_random_position_in_room(width, height, room)
    def get_containing_places(self):
        """Returns all rooms an pathways"""
        return itertools.chain(self.rooms, self.pathways)
    def collide_with_rect(self, obj):
        """Ugly bit of code that requires a previous state to be set"""
        rect2.set_points_from_dimensions(obj.x,
                                               obj.y,
                                               obj.w,
                                               obj.h)
        return rect1.overlaps(rect2)
    def contained_in_a_room(self, x, y, w, h, room):
        """True if the rect defined by the given dimensions is inside the given
room or pathway"""
        rect1.set_points_from_dimensions(x, y, w, h)
        return room.inner_rect.contains(rect1)
    def contained_in_any_room(self, x, y, w, h):
        """True if the rect defined by the given dimensions is inside a room or
pathway"""
        rect1.set_points_from_dimensions(x, y, w, h)
        return any(self.contained_in_a_room(x, y, w, h, r)
                   for r in itertools.chain(self.rooms, self.pathways))
    def collide_with_objects(self, x, y, w, h, ex = None):
        """True if the rect defined by the given dimensions collide with any object
except for ex"""
        rect1.set_points_from_dimensions(x, y, w, h)
        if ex is not None:
            return any(self.collide_with_rect(i) for i in self.placeable_objects()
                       if i != ex and not i.go_through)
        else:
            return any(self.collide_with_rect(i) for i in self.placeable_objects()
                       if not i.go_through)
    def set_location(self, obj, room = None):
        """Assign a random free position to an object. Will try at most 10000
times before raising an exception"""
        width = obj.w
        height = obj.h
        for i in range(10000):
            if room is None:
                x, y = self.get_random_position(width, height)
                contained = self.contained_in_any_room(x, y, width, height)
            else:
                x, y = self.get_random_position_in_room(width, height, room)
                contained = self.contained_in_a_room(x, y, width, height, room)
            if contained:
                if obj.go_through:
                    obj.set_location(x, y)
                    return
                elif not self.collide_with_objects(x, y, width, height):
                    obj.set_location(x, y)
                    return
        raise Exception('Could not assign a position to object: '
                        + str(obj))
    def draw(self):
        for l in self.contents:
            for i in l:
                i.draw()