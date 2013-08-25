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

import pyglet, itertools, random
from pyglet.window import key
from constants import (FIELD_FONT_SIZE as FONT_SIZE, OBJECT_FONT_SIZE,
                       ST_BOUND_Y, ST_BOUND_X, OBJECT_FONT_FACE, WALL_WIDTH,
                       EDGES)
from random import randint
from rect import Rect, Point

pointa = Point(0, 0)
pointb = Point(0, 0)
flatten = itertools.chain.from_iterable
ran = range
def range(*args):
    """Beefed out version of range that automatically deals
with reverse direction"""
    if len(args) == 3:
        return ran(*args)
    elif len(args) == 2:
        if args[0] <= args[1]:
            return ran(args[0], args[1])
        else:
            return ran(args[0] - 1, args[1] - 1, -1)
    elif len(args) == 1:
        return ran(args[0])
    elif len(args) == 0:
        raise TypeError('range takes at least 1 argument (0 given)')
    else:
        raise TypeError('range takes at most 3 arguments (0 given)'.format([str(len(args))]))

def range_inc(*args):
    """Like range but inclusive"""
    if len(args) == 3:
        if args[0] <= args[1]:
            return ran(args[0], args[1] + 1, args[2])
        else:
            return ran(args[0], args[1] - 1, args[2])
    elif len(args) == 2:
        if args[0] <= args[1]:
            return ran(args[0], args[1] + 1)
        else:
            return ran(args[0], args[1] - 1, -1)
    elif len(args) == 1:
        return ran(args[0] + 1)
    elif len(args) == 0:
        raise TypeError('range takes at least 1 argument (0 given)')
    else:
        raise TypeError('range takes at most 3 arguments (0 given)'.format([str(len(args))]))

class SubscriptionFound(Exception):
    pass

class UnplaceableRoomException(Exception):
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
                 stationary = False, hostile = True, go_through = False, range = 1):
        super(CreatureDefinition, self).__init__(id, go_through, symbol, description)
        self.health = health
        self.speed = speed
        self.hostile = hostile
        self.stationary = stationary
        self.range = range
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
    def set_location(self, x, y):
        self.sprite.x = x
        self.sprite.y = y

class Creature(Object):
    """Actual creature on the screen"""
    def __init__(self, definition):
        super(Creature, self).__init__(definition)
        self.intended_x = self.sprite.x
        self.intended_y = self.sprite.y
    def update(self, dt):
        if not self.definition.stationary:
            if self.definition.hostile:
                if self.within_range():
                    self.attack()
                else:
                    if self.target is not None:
                        self.chase()
            else:
                self.roam()
    def within_range(self):
        pointa.x = self.sprite.x + self.sprite.content_width / 2
        pointa.y = self.sprite.y + self.sprite.content_height / 2
        pointb.x = self.target.sprite.x + self.sprite.content_width / 2
        pointb.y = self.target.sprite.y + self.sprite.content_height / 2
        return (pointa.distance_to(pointb) <= self.definition.range
                +  max(self.sprite.content_height, self.sprite.content_width) / 2)
    def attack(self):
        pass
    def chase(self):
        ox = self.sprite.x
        oy = self.sprite.y
        x = self.target.sprite.x
        y = self.target.sprite.y
        mov_x = min(abs(x - ox), self.definition.speed)
        mov_y = min(abs(y - oy), self.definition.speed)
        nx = self.sprite.x + mov_x * (1 if x > ox else -1)
        ny = self.sprite.y + mov_y * (1 if y > oy else -1)
        self.intent(nx, ny)
    def movements(self):
        """Iterator function that returns all the possible positions in the
intended direction"""
        for i in reversed(range_inc(self.sprite.x,
                                    self.intended_x)):
            for j in reversed(range_inc(self.sprite.y,
                                        self.intended_y)):
                yield (i, j)
    def set_location(self, x, y):
        super(Creature, self).set_location(x, y)
        self.intent(x, y)
    def intent(self, x, y):
        self.intended_x = x
        self.intended_y = y

class Hero(Creature):
    def __init__(self, khandler, lvl = 0, inv = None):
        d = ObjectDefinition(-1, False, '@', 'You')
        super(Hero, self).__init__(d)
        self.lvl = lvl
        self.inv = inv
        self.khandler = khandler
        self.speed = 3
        if inv is None:
            self.inv = []
    def update(self, dt):
        if self.khandler[key.UP]:
            self.intended_y = self.sprite.y + self.speed
        if self.khandler[key.DOWN]:
            self.intended_y = self.sprite.y - self.speed
        if self.khandler[key.LEFT]:
            self.intended_x = self.sprite.x - self.speed
        if self.khandler[key.RIGHT]:
            self.intended_x = self.sprite.x + self.speed

class StageDefinition(object):
    def __init__(self, obj_definitions, room_definitions,
                 creature_definitions):
        self.obj_definitions = obj_definitions
        self.room_definitions = room_definitions
        self.creature_definitions = creature_definitions

class Stage(Container):
    def __init__(self, stage_def, hero, min_room_dim = (50, 50),
                 max_room_dim = (100, 100), rand_room_no = 0):
        self.min_room_dim = min_room_dim
        self.max_room_dim = max_room_dim
        self.random_room_no = rand_room_no
        self.rooms = []
        self.create_rooms(stage_def.room_definitions)
        self.objects = Object.from_list(stage_def.obj_definitions)
        self.creatures = Creature.from_list(stage_def.creature_definitions)
        self.creatures.append(hero)
        self.contents = []
        self.hero = hero
        self.contents.extend(self.rooms)
        self.contents.extend(self.objects)
        self.contents.extend(self.creatures)
        super(Stage, self).__init__(self.contents)
        self.rect_1 = Rect.from_dimensions(0, 0, 0, 0)
        self.rect_2 = Rect.from_dimensions(0, 0, 0, 0)
        self.arrange_objects()
        self.set_enemies()
    def create_rooms(self, room_definitions):
        d = self.random_room_dimension()
        x = (ST_BOUND_X - d[0]) / 2
        y = (ST_BOUND_Y - d[1]) / 2
        free_edges = []
        self.place_room(None, d, (x, y), free_edges, None)
        l = list(itertools.chain(room_definitions,
                                 range(self.random_room_no)))
        random.shuffle(l)
        for i in l:
            try:
                edges_clone = free_edges [:]
                random.shuffle(edges_clone)
                for edge in edges_clone:
                    dim_counter = 100
                    while dim_counter > 0:
                        dim_counter -= 1
                        dim = self.get_room_dimension(i)
                        pos_counter = min(100, self.min_room_dim[0], self.min_room_dim[1])
                        while pos_counter > 0:
                            pos_counter -= 1
                            pos = self.get_random_room_position(edge, dim)
                            if self.placement_possible(dim, pos):
                                pos_counter = 0
                                dim_counter = 0
                                stop_iter = True
                    if stop_iter:
                        break
                self.place_room(i, dim, pos, free_edges, edge)
            except UnplaceableRoomException, ex:
                if type(i) == RoomDefinition:
                    raise ex
                else:
                    pass
    def placement_possible(self, dimension, position):
        return True
    def get_random_room_position(self, edge, dimension):
        """Returns a random room position relative to an edge"""
        if edge[1] == 1: #Left position
            y = randint(edge[0].y, edge[0].y + edge[0].h)
            x = edge[0].x - (2 * WALL_WIDTH + dimension[0])
        elif edge[1] == 2: #Top
            x = randint(edge[0].x, edge[0].x + edge[0].w)
            y = edge[0].y + edge[0].h + 2 * WALL_WIDTH
        elif edge[1] == -1: #Right
            y = randint(edge[0].y, edge[0].y + edge[0].h)
            x = edge[0].x + edge[0].h + 2 * WALL_WIDTH + dimension[0]
        elif edge[1] == -2: #Bottom
            x = randint(edge[0].x, edge[0].x + edge[0].w)
            y = edge[0].y - (2 * WALL_WIDTH - dimension[1])
        return x, y
        #return self.get_random_position(dimension[0], dimension[1])
    def get_room_dimension(self, definition = None):
        if type(definition) == RoomDefinition:
            return (definition.w, definition.h)
        else:
            return self.random_room_dimension()
    def random_room_dimension(self):
        """Returns a random height and width for a room"""
        w = randint(self.min_room_dim[0], self.max_room_dim[0])
        h = randint(self.min_room_dim[1], self.max_room_dim[1])
        return w, h
    def place_room(self, definition, dimension, pos, free_edges, parent):
        """Place a random or predefined room"""
        if type(definition) != RoomDefinition:
            definition = RoomDefinition(dimension[0], dimension[1])
        room = Room(definition, pos[0], pos[1])
        self.rooms.append(room)
        def edge_tups():
            return map(lambda x: (room, x), EDGES)
        if(parent is None):
            free_edges.extend(edge_tups())
        else:
            free_edges.extend(filter(lambda x: parent[1] != x[1], edge_tups()))
            room.add_entrance(-parent[1])
            free_edges.remove(parent)
    def set_enemies(self):
        for i in self.creatures:
            try:
                if i.definition.hostile:
                    i.target = self.hero
            except AttributeError:
                pass
    def update(self, dt):
        for obj in self.placeable_objects():
            try:
                obj.update(dt)
                if not obj.definition.go_through:
                    w = obj.sprite.content_width
                    h = obj.sprite.content_height
                    for i in obj.movements():
                        if (self.contained_in_room(i[0], i[1], w, h)
                            and not self.collide_with_objects(i[0], i[1], w, h, obj)):
                            obj.sprite.x = i[0]
                            obj.sprite.y = i[1]
                            break
                        else:
                            pass
            except AttributeError:
                pass
    def placeable_objects(self):
        return itertools.chain(self.objects, self.creatures)
    def arrange_objects(self):
        """Set initial arrangement of the objects"""
        for obj in self.placeable_objects():
            self.set_location(obj)
    def get_random_position(self, width, height):
        """Returns a random point in the map"""
        x = randint(0, ST_BOUND_X - width)
        y = randint(0, ST_BOUND_Y - height)
        return x, y
    def collide_with_rect(self, obj):
        """Ugly bit of code that requires a previous state to be set"""
        self.rect_2.set_points_from_dimensions(obj.sprite.x,
                                               obj.sprite.y,
                                               obj.sprite.content_width,
                                               obj.sprite.content_height)
        return self.rect_1.overlaps(self.rect_2)
    def contained_in_room(self, x, y, w, h):
        """True if the rect defined by the given dimensions is inside a room"""
        self.rect_1.set_points_from_dimensions(x, y, w, h)
        return any(i.inner_rect.contains(self.rect_1) for i in self.rooms)
    def collide_with_objects(self, x, y, w, h, ex = None):
        self.rect_1.set_points_from_dimensions(x, y, w, h)
        if ex is not None:
            return any(self.collide_with_rect(i) for i in self.placeable_objects()
                       if i != ex and not i.definition.go_through)
        else:
            return any(self.collide_with_rect(i) for i in self.placeable_objects()
                       if not i.definition.go_through)
    def set_location(self, obj):
        """Assign a random free position to an object. Will try at most 10000
times before raising an exception"""
        width = obj.sprite.content_width
        height = obj.sprite.content_height
        for i in range(10000):
            x, y = self.get_random_position(width, height)
            if (self.contained_in_room(x, y, width, height)):
                if obj.definition.go_through:
                    obj.set_location(x, y)
                    return
                elif not self.collide_with_objects(x, y, width, height):
                    obj.set_location(x, y)
                    return
        raise Exception('Could not assign a position to object: '
                        + str(obj))

class RoomDefinition(object):
    def __init__(self, w, h, obj_definitions = [], creature_definitions = []):
        self.obj_definitions = obj_definitions
        self.creature_definitions = creature_definitions
        self.w = w
        self.h = h

class Room(Container):
    def __init__(self, room_def, x, y):
        self.room_def = room_def
        self.x = x
        self.y = y
        w = room_def.w
        h = room_def.h
        self.w = w
        self.h = h
        self.lwall = pyglet.graphics.vertex_list(4, ('v2i', (x, y, x + WALL_WIDTH, y, x, y + h, x + WALL_WIDTH, y + h)))
        self.twall = pyglet.graphics.vertex_list(4, ('v2i', (x, y + h, x + w, y + h, x, y + h + WALL_WIDTH, x + w, y + h + WALL_WIDTH)))
        self.bwall = pyglet.graphics.vertex_list(4, ('v2i', (x, y, x + w, y, x, y + WALL_WIDTH, x + w, y + WALL_WIDTH)))
        self.rwall = pyglet.graphics.vertex_list(4, ('v2i', (x + w, y, x + w + WALL_WIDTH, y, x + w, y + h + WALL_WIDTH, x + w + WALL_WIDTH, y + h + WALL_WIDTH)))
        self.inner_rect = Rect(Point(x + WALL_WIDTH, y + WALL_WIDTH),
                               Point(x + w, y + h))
    def draw(self):
        self.lwall.draw(pyglet.gl.GL_QUAD_STRIP)
        self.twall.draw(pyglet.gl.GL_QUAD_STRIP)
        self.bwall.draw(pyglet.gl.GL_QUAD_STRIP)
        self.rwall.draw(pyglet.gl.GL_QUAD_STRIP)
    def add_entrance(self, entrance):
        pass

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
