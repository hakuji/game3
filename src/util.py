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
from constants import (FIELD_FONT_SIZE as FONT_SIZE, OBJECT_FONT_SIZE,
                       ST_BOUND_Y, ST_BOUND_X, OBJECT_FONT_FACE, WALL_WIDTH,
                       EDGES)
from random import randint
from rect import Rect, Point

pointa = Point(0, 0)
pointb = Point(0, 0)
flatten = itertools.chain.from_iterable
rect1 = Rect.from_dimensions(0, 0, 0, 0)
rect2 = Rect.from_dimensions(0, 0, 0, 0)

ran = range
def range(*args):
    """Beefed out version of range that automatically deals
    with reverse direction

    range([start,] stop[, step]) -> list of integers

    Return a list containing an arithmetic progression of integers.
    range(i, j) returns [i, i+1, i+2, ..., j-1]; start (!) defaults to 0.
    When step is given, it specifies the increment (or decrement).
    For example, range(4) returns [0, 1, 2, 3].  The end point is omitted!
    These are exactly the valid indices for a list of 4 elements."""
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

def vertex_list_from_rect(x, y, w, h, color = (0, 0, 255)):
    r, g, b = color
    return pyglet.graphics.vertex_list(
        4, ('v2i', (x,     y,
                    x + w, y,
                    x,     y + h,
                    x + w, y + h)),
        ('c3B', (r, g, b,
                 r, g, b,
                 r, g, b,
                 r, g, b)
        ))

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
                 light_radius, stationary = False, hostile = True,
                 go_through = False, range = 1):
        super(CreatureDefinition, self).__init__(id, go_through, symbol, description)
        self.health = health
        self.speed = speed
        self.hostile = hostile
        self.stationary = stationary
        self.range = range
        self.light_radius = light_radius
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
            if self.definition.hostile and self.target is not None:
                if self.within_range():
                    self.attack()
                else:
                    if self.target_visible():
                        self.chase()
                    else:
                        self.roam()
            else:
                self.roam()
    def within_range(self):
        pointa.x = self.sprite.x + self.sprite.content_width / 2
        pointa.y = self.sprite.y + self.sprite.content_height / 2
        pointb.x = self.target.sprite.x + self.sprite.content_width / 2
        pointb.y = self.target.sprite.y + self.sprite.content_height / 2
        return (pointa.distance_to(pointb) <= self.definition.range
                +  max(self.sprite.content_height, self.sprite.content_width) / 2)
    def target_visible(self):
        x1, y1 = self.target.sprite.x, self.target.sprite.y
        x2, y2 = self.sprite.x, self.sprite.y
        return abs((x1 - x2) + (y1 - y2)) <= self.definition.light_radius
    def roam(self):
        """Move randomly"""
        x, y, s = self.sprite.x, self.sprite.y, self.definition.speed
        self.intent(randint(x - s, x + s), randint(y - s, y + s))
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
    def __init__(self, obj_definitions, room_definitions, pathway_definitions,
                 creature_definitions, min_room_dim = (50, 50),
                 max_room_dim = (100, 100), random_room_no = 0):
        self.obj_definitions = obj_definitions
        self.room_definitions = room_definitions
        self.creature_definitions = creature_definitions
        self.min_room_dim = min_room_dim
        self.max_room_dim = max_room_dim
        self.random_room_no = random_room_no
        self.pathway_definitions = pathway_definitions

class Stage(Container):
    def __init__(self, stage_def, hero):
        self.pathways = map(lambda d: Pathway(*d), stage_def.pathway_definitions)
        self.rooms = stage_def.room_definitions
        self.objects = Object.from_list(stage_def.obj_definitions)
        self.creatures = Creature.from_list(stage_def.creature_definitions)
        self.creatures.append(hero)
        self.arrange_objects()
        self.init_rooms()
        self.hero = hero
        self.set_enemies()
        self.contents = []
        self.contents.extend(self.rooms)
        self.contents.extend(self.pathways)
        self.contents.extend(self.objects)
        self.contents.extend(self.creatures)
        super(Stage, self).__init__(self.contents)
    def init_rooms(self):
        for r in self.rooms:
            creatures = Creature.from_list(r.creature_def)
            for c in creatures:
                self.creatures.append(c)
                self.set_location(c, r)
            objects = Object.from_list(r.object_def)
            for o in objects:
                self.objects.append(o)
                self.set_location(o, r)
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
                        if (self.contained_in_any_room(i[0], i[1], w, h)
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
        rect2.set_points_from_dimensions(obj.sprite.x,
                                               obj.sprite.y,
                                               obj.sprite.content_width,
                                               obj.sprite.content_height)
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
        rect1.set_points_from_dimensions(x, y, w, h)
        if ex is not None:
            return any(self.collide_with_rect(i) for i in self.placeable_objects()
                       if i != ex and not i.definition.go_through)
        else:
            return any(self.collide_with_rect(i) for i in self.placeable_objects()
                       if not i.definition.go_through)
    def set_location(self, obj, room = None):
        """Assign a random free position to an object. Will try at most 10000
times before raising an exception"""
        width = obj.sprite.content_width
        height = obj.sprite.content_height
        for i in range(10000):
            if room is None:
                x, y = self.get_random_position(width, height)
                contained = self.contained_in_any_room(x, y, width, height)
            else:
                x, y = self.get_random_position_in_room(width, height, room)
                contained = self.contained_in_a_room(x, y, width, height, room)
            if contained:
                if obj.definition.go_through:
                    obj.set_location(x, y)
                    return
                elif not self.collide_with_objects(x, y, width, height):
                    obj.set_location(x, y)
                    return
        raise Exception('Could not assign a position to object: '
                        + str(obj))

class Pathway(object):
    def __init__(self, horizontal, x, y, length):
        self.x = x
        self.y = y
        self.length = length
        self.horizontal = horizontal
        if horizontal:
            w = length
            h = self.thickness()
            self.outer_rect = Rect.from_dimensions(
                x + self.thickness() / 2,
                y - WALL_WIDTH,
                w - int(1.08 * self.thickness()),
                h + WALL_WIDTH)
        else:
            w = self.thickness()
            h = length
            self.outer_rect = Rect.from_dimensions(
                x - WALL_WIDTH,
                y + self.thickness() / 2,
                w + WALL_WIDTH,
                h - int(1.45 * self.thickness()))
        self.inner_rect = Rect.from_dimensions(x, y, w, h)
        walls = Room.walls_from_rect(self.outer_rect)
        if horizontal:
            self.awall = walls[1]
            self.bwall = walls[2]
        else:
            self.awall = walls[0]
            self.bwall = walls[3]
        d = self.inner_rect.dimension()
        self.floor = vertex_list_from_rect(d[0], d[1], d[2], d[3], (150, 100, 255))
    def draw(self):
        self.floor.draw(pyglet.gl.GL_QUAD_STRIP)
        self.awall.draw(pyglet.gl.GL_QUAD_STRIP)
        self.bwall.draw(pyglet.gl.GL_QUAD_STRIP)
    @classmethod
    def thickness(cls):
        return WALL_WIDTH * 3

class Room(object):
    def __init__(self, x, y, w, h, obj_def = [], creat_def = []):
        self.object_def = obj_def
        self.creature_def = creat_def
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.inner_rect = Rect.from_dimensions(x + WALL_WIDTH, y + int(WALL_WIDTH * 1.25),
                                               w + WALL_WIDTH, h + int(WALL_WIDTH * 1.5))
        self.outer_rect = Rect.from_dimensions(x, y,
                                               2 * WALL_WIDTH + w,
                                               2 * WALL_WIDTH + h)
        self.walls = self.walls_from_rect(self.outer_rect)
        d = self.inner_rect.dimension()
        self.floor = vertex_list_from_rect(d[0], d[1] - 2, d[2], d[3], (150, 50, 255))
    def draw(self):
        self.floor.draw(pyglet.gl.GL_QUAD_STRIP)
        for w in self.walls:
            w.draw(pyglet.gl.GL_QUAD_STRIP)
    @classmethod
    def walls_from_rect(cls, rect):
        x, y, w, h = rect.dimension()
        left = vertex_list_from_rect(x, y, WALL_WIDTH, WALL_WIDTH + h)
        top = vertex_list_from_rect(x, y + h, w, WALL_WIDTH)
        bottom = vertex_list_from_rect(x, y, w, WALL_WIDTH)
        right = vertex_list_from_rect(x + w, y, WALL_WIDTH, WALL_WIDTH + h)
        return (left, top, bottom, right)

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
