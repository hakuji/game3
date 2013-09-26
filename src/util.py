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

import pyglet, itertools, types, random
from pyglet.window import key
from constants import (FIELD_FONT_SIZE as FONT_SIZE, OBJECT_FONT_SIZE,
                       ST_BOUND_Y, ST_BOUND_X, OBJECT_FONT_FACE, WALL_WIDTH,
                       EDGES, ROAM_LIST)
from random import randint
from rect import Rect, Point
from decorations import autoset

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

class NextLevelException(Exception):
    pass

class GameOverException(Exception):
    def __init__(self, defeat):
        self.defeat = defeat

class ImpossiblePathwayException(Exception):
    pass

class ReplaceObjectException(Exception):
    def __init__(self, this, that):
        self.this = this
        self.that = that

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

class Option(Drawable, Reactable):
    """Option accessed with a key"""
    @autoset
    def __init__(self, subs, description, sprite):
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

def empty_interaction(self):
    pass

class ObjectDefinition(object):
    """The common properties of a type of object"""
    @autoset
    def __init__(self, go_through, symbol, description,
                 interaction = empty_interaction, range = 1):
        self.screenClass = Object
    def toScreen(self, count = None):
        if count == None:
            return self.screenClass(self)
        else:
            return [self.screenClass(self) for i in range(count)]

class CreatureDefinition(ObjectDefinition):
    """The common properties of a creature"""
    @autoset
    def __init__(self, symbol, description, health, speed, strength,
                 light_radius, stationary = False, hostile = True,
                 go_through = False, range = 1, interaction=empty_interaction):
        super(CreatureDefinition, self).__init__(
            go_through, symbol, description, interaction, range)
        self.screenClass = Creature

class Object(Drawable):
    """Actual object on the screen"""
    @classmethod
    def from_list(cls, l):
        def fun():
            for d in l:
                if isinstance(d, ObjectDefinition):
                    yield d.toScreen()
                else:
                    for o in d[0].toScreen(d[1]):
                        yield o
        return list(fun())
    @autoset
    def __init__(self, definition):
        sprite = pyglet.text.Label(
            definition.symbol,
            font_name=OBJECT_FONT_FACE,
            font_size=OBJECT_FONT_SIZE)
        self.interact = types.MethodType(definition.interaction, self)
        super(Object, self).__init__(sprite)
    def set_location(self, x, y):
        self.sprite.x = x
        self.sprite.y = y
    def update(self):
        pass
    def within_distance(self, obj, distance):
        """If obj is at most distance from self return true"""
        pointa.x = self.sprite.x + self.sprite.content_width / 2
        pointa.y = self.sprite.y + self.sprite.content_height / 2
        pointb.x = obj.sprite.x + obj.sprite.content_width / 2
        pointb.y = obj.sprite.y + obj.sprite.content_height / 2
        return (pointa.distance_to(pointb) <= distance
                +  max(self.sprite.content_height, self.sprite.content_width) / 2)
    def within_range(self, obj):
        return self.within_distance(obj, self.definition.range)

class Creature(Object):
    """Actual creature on the screen"""
    def __init__(self, definition):
        super(Creature, self).__init__(definition)
        self.intended_x = self.sprite.x
        self.intended_y = self.sprite.y
        self.target = None
        self.last_desired_direction = [0, 0]
        self.change_countdown = 0
        self.last_desired_speed = 1
        self.health = self.definition.health
    def be_attacked(self, other):
        """Be attacked by another creature"""
        self.health -= other.definition.strength
    def dead(self):
        return self.health <= 0
    def update(self):
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
    def continue_last_desired(self):
        """Return true if the creature should continue moving towards where it
was moving before."""
        return self.change_countdown > 0
    def within_range(self, obj = None):
        if obj is None:
            return super(Creature, self).within_range(self.target)
        else:
            return super(Creature, self).within_range(obj)
    def target_visible(self):
        return self.within_distance(self.target, self.definition.light_radius)
    def roam(self):
        """Move randomly"""
        x, y = self.sprite.x, self.sprite.y
        self.change_countdown -= 1
        if not self.continue_last_desired():
            dx = random.choice(ROAM_LIST)
            dy = random.choice(ROAM_LIST)
            self.set_last_desired_direction(dx, dy, 1)
        self.move_towards(
            (self.last_desired_direction[0] * self.last_desired_speed) + x,
            (self.last_desired_direction[1] * self.last_desired_speed) + y)
    def set_last_desired_direction(self, dx, dy, speed):
        """Set the last direction followed and the time until change"""
        self.last_desired_direction[0] = dx
        self.last_desired_direction[1] = dy
        self.last_desired_speed = speed
        self.change_countdown = self.definition.light_radius
    def attack(self):
        self.target.be_attacked(self)
    def chase(self):
        """Chase and set the last desired point"""
        x = self.target.sprite.x
        y = self.target.sprite.y
        dx = - cmp(self.sprite.x - x, 0)
        dy = - cmp(self.sprite.y - y, 0)
        self.set_last_desired_direction(dx, dy, self.definition.speed)
        self.move_towards(x, y)
    def move_towards(self, x, y):
        """Move towards a point"""
        ox = self.sprite.x
        oy = self.sprite.y
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
    @autoset
    def __init__(self, khandler, inv = None):
        d = CreatureDefinition(symbol='@',
                               description='You',
                               health=100,
                               speed=3,
                               strength=3,
                               light_radius=20,
                               go_through=False,
                               range=6)
        super(Hero, self).__init__(d)
        self.speed = 3
        self.intended_interact = False
        if inv is None:
            self.inv = []
    def update(self):
        if self.dead():
            raise GameOverException(True)
        self.intended_interact = False
        if self.khandler[key.W]:
            self.intended_y = self.sprite.y + self.speed
        if self.khandler[key.S]:
            self.intended_y = self.sprite.y - self.speed
        if self.khandler[key.A]:
            self.intended_x = self.sprite.x - self.speed
        if self.khandler[key.D]:
            self.intended_x = self.sprite.x + self.speed
        if self.khandler[key.J]:
            self.intended_interact = True

class StageDefinition(object):
    @autoset
    def __init__(self, obj_definitions, rooms, pathways,
                 creature_definitions, min_room_dim = (50, 50),
                 max_room_dim = (100, 100), random_room_no = 0):
        pass

class Stage(Container):
    def __init__(self, stage_def, hero):
        self.pathways = stage_def.pathways
        self.rooms = stage_def.rooms
        self.objects = Object.from_list(stage_def.obj_definitions)
        self.creatures = Creature.from_list(stage_def.creature_definitions)
        self.arrange_objects()
        self.hero = hero
        self.init_rooms()
        self.set_enemies()
        self.contents = []
        self.contents.extend(self.rooms)
        self.contents.extend(self.pathways)
        self.contents.extend(self.objects)
        self.contents.extend(self.creatures)
        super(Stage, self).__init__(self.contents)
    def init_rooms(self):
        for r in self.rooms:
            if r.start:
                self.set_location(self.hero, r)
            self.creatures.append(self.hero)
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
    def remove_object(self, obj):
        self.objects.remove(obj)
        self.contents.remove(obj)
    def create_object(self, definition, x, y):
        """Create and place an object"""
        obj = definition.toScreen()
        self.objects.append(obj)
        self.contents.append(obj)
        obj.set_location(x, y)
    def replace_object(self, ex):
        """Use a replace exception to replace an object"""
        for o in self.objects:
            if o.definition == ex.this:
                self.remove_object(o)
                self.create_object(ex.that, o.sprite.x, o.sprite.y)
                return
    def update(self):
        for obj in self.placeable_objects():
            obj.update()
        self.update_movements()
        try:
            self.hero_interact()
        except ReplaceObjectException as ex:
            self.replace_object(ex)
    def hero_interact(self):
        if self.hero.intended_interact:
            for o in self.placeable_objects():
                if o == self.hero:
                    continue
                if o.within_range(self.hero):
                    o.interact()
                    return
    def update_movements(self):
        for c in self.creatures:
            if not c.definition.go_through:
                w = c.sprite.content_width
                h = c.sprite.content_height
                for i in c.movements():
                    if (self.contained_in_any_room(i[0], i[1], w, h)
                        and not self.collide_with_objects(i[0], i[1], w, h, c)):
                        c.sprite.x = i[0]
                        c.sprite.y = i[1]
                        break
                    else:
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
        """True if the rect defined by the given dimensions collide with any object
except for ex"""
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
    @autoset
    def __init__(self, horizontal, x, y, length):
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

class MagneticPathway(Pathway):
    def is_left(self):
        """Return true if r1 is left of r2"""
        return self.r1.inner_rect.right < self.r2.inner_rect.left
    def is_right(self):
        """Return true if r1 is right of r2"""
        return self.r2.inner_rect.right < self.r1.inner_rect.left
    def is_bottom(self):
        """Return true if r1 is bottom of r2"""
        return self.r1.inner_rect.top < self.r2.inner_rect.bottom
    def is_top(self):
        """Return true if r1 is top of r2"""
        return self.r2.inner_rect.top < self.r1.inner_rect.bottom
    def __init__(self, room1, room2):
        self.r1 = room1
        self.r2 = room2
        l, r, b, t = self.is_left(), self.is_right(), self.is_bottom(), self.is_top()
        if not (l or r or b or t):
            # A pathway on top of another
            raise ImpossiblePathwayException()
        elif (l or r) and (t or b):
            # A pathway at the corner of another
            raise ImpossiblePathwayException()
        else:
            if (b or t):
                if b:
                    tr = self.r2
                    br = self.r1
                else:
                    tr = self.r1
                    br = self.r2
                y = br.inner_rect.top - int(1.5 * WALL_WIDTH)
                height = tr.inner_rect.bottom - y + int(1.5 * WALL_WIDTH)
                min_x = max(br.inner_rect.left, tr.inner_rect.left)
                max_x = min(br.inner_rect.right, tr.inner_rect.right) - self.thickness()
                x = randint(min_x, max_x)
                super(MagneticPathway, self).__init__(False, x, y,  height)
            else:
                if l:
                    lr = self.r1
                    rr = self.r2
                else:
                    lr = self.r2
                    rr = self.r1
                x = lr.inner_rect.right - int(1.5 * WALL_WIDTH)
                width = rr.inner_rect.left - x + int(1.5 * WALL_WIDTH)
                min_y = max(lr.inner_rect.bottom, rr.inner_rect.bottom) - 2
                max_y = min(lr.inner_rect.top, rr.inner_rect.top) - self.thickness() - WALL_WIDTH + 3
                y = randint(min_y, max_y)
                super(MagneticPathway, self).__init__(True, x, y,  width)


class Room(object):
    @autoset
    def __init__(self, x, y, w, h, object_def = [], creature_def = [],
                 start  = False):
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
