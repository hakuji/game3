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
from constants import (OBJECT_FONT_SIZE,
                       ST_BOUND_Y, ST_BOUND_X, OBJECT_FONT_FACE, WALL_WIDTH,
                       EDGES, ROAM_LIST, HITBOX_GAP)
from random import randint
from rect import Rect, Point
from decorations import autoset
from exception import (
    SubscriptionFound, GameOverException,
    ReplaceObjectException,
    ImpossiblePathwayException,
    CreatureDeathException)
from function import range, range_inc, vertex_list_from_rect

pointa = Point(0, 0)
pointb = Point(0, 0)
flatten = itertools.chain.from_iterable
rect1 = Rect.from_dimensions(0, 0, 0, 0)
rect2 = Rect.from_dimensions(0, 0, 0, 0)

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

def empty_interaction(self):
    pass

class Object(Drawable):
    """Actual object on the screen"""
    @classmethod
    def from_list(cls, l):
        def fun():
            for d in l:
                if isinstance(d, tuple):
                    for i in range(d[1]):
                        yield d[0]()
                else:
                    yield d()
        return list(fun())
    @autoset
    def __init__(self, go_through, symbol, description,
                 interact = empty_interaction, range = 1, id = None):
        sprite = pyglet.text.Label(
            symbol,
            font_name=OBJECT_FONT_FACE,
            font_size=OBJECT_FONT_SIZE)
        self.interact = types.MethodType(interact, self)
        super(Object, self).__init__(sprite)
        self.rect_ = Rect.from_dimensions(0, 0, self.w, self.h)
    @property
    def x(self):
        return self.sprite.x
    @x.setter
    def x(self, value):
        self.sprite.x = value
    @x.deleter
    def x(self):
        del self.sprite.x
    @property
    def y(self):
        return self.sprite.y - 2
    @y.setter
    def y(self, value):
        self.sprite.y = value + 2
    @y.deleter
    def y(self):
        del self.sprite.y
    @property
    def w(self):
        return self.sprite.content_width
    @w.setter
    def w(self, value):
        self.sprite.content_width = value
    @w.deleter
    def w(self):
        del self.sprite.content_width
    @property
    def h(self):
        return self.sprite.content_height - 3
    @h.setter
    def h(self, value):
        self.sprite.content_height = value
    @h.deleter
    def h(self):
        del self.sprite.content_height
    @property
    def rect(self):
        self.rect_.set_points_from_dimensions(
            self.x,
            self.y,
            self.w,
            self.h)
        return self.rect_
    def set_location(self, x, y):
        self.x = x
        self.y = y
    def update(self):
        pass
    def within_distance(self, obj, distance):
        """If obj is at most distance from self return true"""
        pointa.x = self.x + self.w / 2
        pointa.y = self.y + self.h / 2
        pointb.x = obj.x + obj.w / 2
        pointb.y = obj.y + obj.h / 2
        return (pointa.distance_to(pointb) <= distance
                +  max(self.h, self.w) / 2)
    def within_range(self, obj):
        return self.within_distance(obj, self.range)
    def draw(self):
        x, y = self.x, self.y
        w, h = self.w, self.h
        rect = vertex_list_from_rect(x, y, w, h)
        rect.draw(pyglet.gl.GL_QUAD_STRIP)
        super(Object, self).draw()
    def __str__(self):
        return self.symbol + ' ' + self.description

class Direction(object):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'

class Creature(Object):
    """Actual creature on the screen"""
    @autoset
    def __init__(self, symbol, description, health, speed, strength,
                 light_radius, attack_type, stationary = False, hostile = True,
                 go_through = False, range = 1, interaction=empty_interaction,
                 cooldown_ = 10):
        super(Creature, self).__init__(
            go_through,
            symbol,
            description,
            interaction,
            range
        )
        self.intended_x = self.x
        self.intended_y = self.y
        self.target = None
        self.last_desired_direction = [0, 0]
        self.change_countdown = 0
        self.last_desired_speed = 1
        self.health = self.health
        self.cooldown = 0
        self.facing = [None, Direction.NORTH]
        self.hitbox = None
    def be_attacked(self, other):
        """Be attacked by another creature"""
        self.health -= other.strength
    def dead(self):
        return self.health <= 0
    def update(self):
        if self.dead():
            raise CreatureDeathException()
        if not self.stationary:
            if self.hostile and self.target is not None:
                if self.within_range():
                    self.set_facing(self.target_direction())
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
        return self.within_distance(self.target, self.light_radius)
    def roam(self):
        """Move randomly"""
        x, y = self.x, self.y
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
        self.change_countdown = self.light_radius
        self.set_facing(self.last_desired_direction)
    def set_facing(self, direction):
        if direction == [0, 0]:
            return
        if direction[0] == 1:
            self.facing[0] = Direction.EAST
        elif direction[0] == -1:
            self.facing[0] = Direction.WEST
        else:
            self.facing[0] = None
        if direction[1] == 1:
            self.facing[1] = Direction.NORTH
        elif direction[1] == -1:
            self.facing[1] = Direction.SOUTH
        else:
            self.facing[1] = None
    def attack(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            self.cooldown = self.cooldown_
            self.set_hitbox()
    def set_hitbox(self):
        w = h = self.range
        x = self.x
        y = self.y
        if self.facing[0] == Direction.EAST:
            x += self.w + HITBOX_GAP
        elif self.facing[0] == Direction.WEST:
            x -= w + HITBOX_GAP
        if self.facing[1] == Direction.NORTH:
            y += self.h + HITBOX_GAP
        elif self.facing[1] == Direction.SOUTH:
            y -=  h + HITBOX_GAP
        self.hitbox = self.attack_type(self, x, y, w, h)
    def chase(self):
        """Chase and set the last desired point"""
        dx, dy = self.target_direction()
        self.set_last_desired_direction(dx, dy, self.speed)
        self.move_towards(self.target.x, self.target.y)
    def target_direction(self):
        dx = cmp(0, self.x - self.target.x)
        dy = cmp(0, self.y - self.target.y)
        return (dx, dy)
    def move_towards(self, x, y):
        """Move towards a point"""
        ox = self.x
        oy = self.y
        mov_x = min(abs(x - ox), self.speed)
        mov_y = min(abs(y - oy), self.speed)
        nx = self.x + mov_x * (1 if x > ox else -1)
        ny = self.y + mov_y * (1 if y > oy else -1)
        self.intent(nx, ny)
    def movements(self):
        """Iterator function that returns all the possible positions in the
intended direction"""
        for i in reversed(range_inc(self.x,
                                    self.intended_x)):
            for j in reversed(range_inc(self.y,
                                        self.intended_y)):
                yield (i, j)
    def set_location(self, x, y):
        super(Creature, self).set_location(x, y)
        self.intent(x, y)
    def intent(self, x, y):
        self.intended_x = x
        self.intended_y = y

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

class Hero(Creature):
    @autoset
    def __init__(self, khandler, inv = None):
        super(Hero, self).__init__(
            symbol='@',
            description='You',
            health=100,
            speed=3,
            strength=3,
            light_radius=20,
            go_through=False,
            range=10,
            cooldown_=3,
            attack_type=MeleeHitbox)
        self.speed = 3
        self.intended_interact = False
        if inv is None:
            self.inv = []
    def update(self):
        if self.dead():
            raise GameOverException(True)
        self.intended_interact = False
        facing = [None, None]
        if self.khandler[key.W]:
            self.intended_y = self.y + self.speed
            facing[1] = Direction.NORTH
        if self.khandler[key.S]:
            self.intended_y = self.y - self.speed
            facing[1] = Direction.SOUTH
        if self.khandler[key.A]:
            self.intended_x = self.x - self.speed
            facing[0] = Direction.WEST
        if self.khandler[key.D]:
            self.intended_x = self.x + self.speed
            facing[0] = Direction.EAST
        if self.khandler[key.J]:
            self.intended_interact = True
        if self.khandler[key.I]:
            self.attack()
        if facing != [None, None]:
            self.facing = facing

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
    def __init__(self, x, y, w, h, objects = [], creatures = [],
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
