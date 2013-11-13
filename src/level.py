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

import itertools, fog, math
from random import randint
from exception import (
    ReplaceObject,
    CreatureDeath,
    CreateObject,
    AppendMessage,
    AddPathway,
    EventList,
    RemovePathway
)
from util import Container, ObjectMessage
from obj import Object
from decorations import autoset
from constants import DEBUG
from function import movements

class Level(Container):
    """A game level, stage etc"""
    @autoset
    def __init__(self, hero, objects, rooms, pathways,
                 creatures, triggers):
        self.objects = Object.from_list(objects)
        self.creatures = Object.from_list(creatures)
        self.hitboxes = []
        self.contents = []
        self.contents.append(self.rooms)
        self.contents.append(self.pathways)
        self.contents.append(self.objects)
        self.contents.append(self.hitboxes)
        self.contents.append(self.creatures)
        self.creatures.append(self.hero)
        self.set_visual()
        self.arrange_objects()
        self.init_rooms()
        self.set_enemies()
        self.set_triggers()
        self.fog_matrix = fog.FogMatrix()
        self.update_fog()
        self.messages = []
        self.hero_saw = []
        super(Level, self).__init__(self.contents)
    def init_rooms(self):
        for r in self.rooms:
            if r.start:
                self.init_start_room(r)
            def set_attributes(l, container):
                objs = Object.from_list(l)
                for o in objs:
                    container.append(o)
                    o.set_visual()
                    self.set_location(o, r)
            set_attributes(r.creatures, self.creatures)
            set_attributes(r.objects, self.objects)
    def init_start_room(self, r):
        stairs = filter(lambda o: o.id == -2, self.objects)
        stairs = stairs[0]
        x = stairs.x
        y = stairs.y
        self.hero.set_location(x, y)
    def set_enemies(self):
        for i in self.creatures:
            if getattr(i, 'hostile', False):
                i.target = self.hero
    def set_triggers(self):
        def obj_from_id(oid):
            compare_ids = lambda obj: obj.id == oid
            return filter(compare_ids, self.placeable_objects())
        for t in self.triggers:
            pred_objs = []
            trigger_objs = []
            for oid in t.predicate.object_ids:
                pred_objs.extend(obj_from_id(oid))
            for oid in t.object_ids:
                trigger_objs.extend(obj_from_id(oid))
            t.set_objects(pred_objs, trigger_objs)
    def remove_object(self, obj):
        self.objects.remove(obj)
    def add_object(self, obj, x = None, y = None):
        """Add and place an object"""
        if x is None:
            obj = obj()
            obj.set_visual()
        else:
            obj.set_visual()
            obj.set_location(x, y)
        self.objects.append(obj)
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
        self.hero_interact()
        self.update_triggers()
        self.update_messages()
    def update_fog(self):
        self.fog_matrix.update(self.hero.x, self.hero.y, self.hero.light_radius)
    def handle_events(self, fun):
        try:
            fun()
        except ReplaceObject as ex:
            self.replace_object(ex)
        except CreateObject as ex:
            self.add_object(ex.obj)
        except AppendMessage as ex:
            self.messages.append(ex.message)
        except AddPathway as ex:
            ex.pathway.set_visual()
            self.pathways.append(ex.pathway)
        except RemovePathway as ex:
            self.pathways.remove(ex.pathway)
        except EventList as ev:
            def raise_ev(ev):
                def f():
                    raise ev
                return f
            for i in ev.events:
                self.handle_events(raise_ev(i))
    def update_triggers(self):
        for t in self.triggers:
            self.handle_events(t.update)
    def update_creatures(self):
        for c in self.creatures[:]:
            try:
                c.update()
                self.update_position(c)
                self.add_hitbox(c)
            except CreatureDeath:
                self.creatures.remove(c)
    def update_messages(self):
        for o in self.placeable_objects():
            if (o not in self.hero_saw
                and self.hero.within_range(o)
                and o != self.hero):
                self.hero_saw.append(o)
                self.messages.append(
                    ObjectMessage('You see a {0}({1})', o))
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
                    self.handle_events(o.on_interact)
                    return
    def update_position(self, creature):
        if not creature.go_through:
            for i in movements(creature.x, creature.y, creature.intended_x,
                               creature.intended_y):
                creature.set_location(*i)
                if (self.contained_in_any_room(creature)
                    and not self.collide_with_objects(creature)):
                    if creature == self.hero:
                        self.update_fog()
                    else:
                        x = creature.x
                        y = creature.y
                        x1 = self.hero.x
                        y1 = self.hero.y
                        if math.hypot(x1 - x, y1 - y) <= self.hero.light_radius or DEBUG:
                            creature.visible_ = True
                        else:
                            creature.visible_ = False
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
    def collide_with_rect(self, obj1, obj2):
        """Ugly bit of code that requires a previous state to be set"""
        return obj1.rect.overlaps(obj2.rect)
    def contained_in_a_room(self, obj, room):
        """True if the rect defined by the given dimensions is inside the given
room or pathway"""
        return room.inner_rect.contains(obj.rect)
    def contained_in_any_room(self, obj):
        """True if the rect defined by the given dimensions is inside a room or
pathway"""
        return any(self.contained_in_a_room(obj, r)
                   for r in itertools.chain(self.rooms, self.pathways))
    def collide_with_objects(self, obj, ignore_go_through = False):
        """True if the rect defined by the given dimensions collide with any object
except for ex"""
        return any(self.collide_with_rect(obj, i) for i in self.placeable_objects()
                   if i != obj and (ignore_go_through or not i.go_through))
    def set_location(self, obj, room = None):
        """Assign a random free position to an object. Will try at most 10000
times before raising an exception"""
        width = obj.w
        height = obj.h
        for i in range(10000):
            if room is None:
                x, y = self.get_random_position(width, height)
                obj.set_location(x, y)
                contained = self.contained_in_any_room(obj)
            else:
                x, y = self.get_random_position_in_room(width, height, room)
                obj.set_location(x, y)
                contained = self.contained_in_a_room(obj, room)
            if contained and not self.collide_with_objects(obj, True):
                return
        raise Exception('Could not assign a position to object: '
                        + str(obj))
    def draw(self):
        for l in self.contents:
            for i in l:
                i.draw()
        if not DEBUG:
            self.fog_matrix.draw()
    def unset_visual(self):
        """Method that unsets all references to the visual representation of an
        object"""
        for i in self.contents:
            for j in i:
                i.unset_visual()
    def set_visual(self):
        """Method that sets the visual representation of an object"""
        for i in self.contents:
            for j in i:
                j.set_visual()
