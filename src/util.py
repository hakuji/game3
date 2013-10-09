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
from pyglet import gl
from pyglet.window import key
from constants import (
    OBJECT_FONT_SIZE,
    OBJECT_FONT_FACE,
    WALL_WIDTH,
    ROAM_LIST,
    HITBOX_GAP,
    INTERACT_COOLDOWN,
    Direction,
    ACCEPT_KEY)
from random import randint
from rect import Rect, Point
from decorations import autoset
from exception import (
    SubscriptionFound, GameOverException,
    ImpossiblePathwayException,
    CreatureDeathException,
    AnimationEnd)
from function import range, range_inc, vertex_list_from_rect

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

def empty_interaction(self):
    pass

class Object(Drawable):
    """Actual object on the screen"""
    pa = Point(0, 0)
    pb = Point(0, 0)
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
    def __init__(self, go_through, symbol, description,
                 interact = empty_interaction, range = 1, id = None, x = 0,
                 y = 0):
        self._set_properties(go_through, symbol, description, interact, range,
                             id)
        sprite = pyglet.text.Label(
            symbol,
            font_name=OBJECT_FONT_FACE,
            font_size=OBJECT_FONT_SIZE)
        self.interact = types.MethodType(interact, self)
        super(Object, self).__init__(sprite)
        self.x = x
        self.y = y
        self.rect_ = Rect.from_dimensions(0, 0, self.w, self.h)
    @autoset
    def _set_properties(self, go_through, symbol, description,
                 interact, range, id):
        """Used during the initialization to autoset attributes"""
        pass
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
        Object.pa.x = self.x + self.w / 2
        Object.pa.y = self.y + self.h / 2
        Object.pb.x = obj.x + obj.w / 2
        Object.pb.y = obj.y + obj.h / 2
        return (Object.pa.distance_to(Object.pb) <= distance
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

class Creature(Object):
    """Actual creature on the screen"""
    @autoset
    def __init__(self, symbol, description, health, speed, strength,
                 light_radius, attack_type, stationary = False, hostile = True,
                 go_through = False, range = 1, interaction=empty_interaction,
                 cooldown_ = 10, roaming = True):
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
    def death(self):
        """Deals with the eventual death of the creature"""
        if self.health <= 0:
            raise CreatureDeathException()
    def update(self):
        self.death()
        self.cooldown = max(0, self.cooldown - 1)
        if not self.stationary:
            if self.hostile and self.target is not None:
                if self.within_range():
                    self.set_facing(self.target_direction())
                    self.attack()
                    return
                else:
                    if self.target_visible():
                        self.chase()
                        return
            if self.roaming:
                self.roam()
                return
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
            pass
        else:
            self.cooldown = self.cooldown_
            self.intended_y = self.y
            self.intended_x = self.x
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
        print x,y
        if self.direction[0] == Direction.EAST:
            x += self.distance
        elif self.direction[0] == Direction.WEST:
            x -= self.distance
        if self.direction[1] == Direction.NORTH:
            y += self.distance
        elif self.direction[1] == Direction.SOUTH:
            y -= self.distance
        print x,y
        return x, y
    def update(self):
        if not self.destination_set:
            self.pos = self.final_destination()
            self.obj.move_towards(self.pos[0], self.pos[1])
            self.destination_set = True
        if self.pos[0] == self.obj.x and self.pos[1] == self.obj.y:
            raise AnimationEnd()

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
            attack_type=MeleeHitbox,
            roaming=False,
            hostile=False
        )
        self.speed = 3
        self.intended_interact = False
        self.animation = None
        self.arrow = self.get_arrow()
        if inv is None:
            self.inv = []
    def draw(self):
        super(Hero, self).draw()
        if self.facing[1] == Direction.NORTH:
            angle = 90.0
            if self.facing[0] == Direction.EAST:
                angle -= 45.0
            elif self.facing[0] == Direction.WEST:
                angle += 45.0
        elif self.facing[1] == Direction.SOUTH:
            angle = 270.0
            if self.facing[0] == Direction.EAST:
                angle += 45.0
            elif self.facing[0] == Direction.WEST:
                angle -= 45.0
        else:
            if self.facing[0] == Direction.EAST:
                angle = 0.0
            elif self.facing[0] == Direction.WEST:
                angle = 180.0
        gl.glPushMatrix()
        gl.glTranslatef(float(self.x + self.w / 2), float(self.y + self.h / 2), 0.0)
        gl.glRotatef(angle, 0.0, 0.0, 1.0)
        self.arrow.draw(pyglet.gl.GL_LINE_STRIP)
        gl.glPopMatrix()
    def get_arrow(self):
        r = b = g = 255
        a = 120
        x1 = self.range + self.w
        x2 = x1 - self.w / 2
        y1 = self.h / 2
        y2 = - (self.h / 2)
        return pyglet.graphics.vertex_list(
            3, ('v2i', (x2,    y2,
                        x1,    0,
                        x2,    y1)),
            ('c4B', (r, g, b, a,
                     r, g, b, a,
                     r, g, b, a)
         ))
    def update(self):
        try:
            super(Hero, self).update()
        except CreatureDeathException:
            raise GameOverException(True)
        if self.animation is not None:
            try:
                self.animation.update()
            except AnimationEnd:
                self.animation = None
            return
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
        if self.khandler[ACCEPT_KEY]:
            if self.cooldown == 0:
                self.intended_interact = True
                self.cooldown = INTERACT_COOLDOWN
            else:
                pass
        if facing != [None, None]:
            self.facing = facing
        if self.khandler[key.J]:
            self.attack()
    def set_animation(self, animation):
        self.animation = animation

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
