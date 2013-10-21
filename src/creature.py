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

import random
from obj import Object, empty_interaction
from exception import CreatureDeathException
from constants import Direction, HITBOX_GAP, ROAM_LIST, ROAM_RATE
from decorations import autoset
from function import range_inc, from_probability_to_bool

class Creature(Object):
    """Actual creature on the screen"""
    @autoset
    def __init__(
            self,
            symbol,
            description,
            health,
            speed,
            strength,
            light_radius,
            attack_type,
            stationary = False,
            hostile = True,
            go_through = False,
            range = 1,
            interaction=empty_interaction,
            cooldown_ = 10,
            roaming = True,
            id = None):
        super(Creature, self).__init__(
            go_through,
            symbol,
            description,
            interaction,
            range,
            id
        )
        self.intended_x = self.x
        self.intended_y = self.y
        self.target = None
        self.last_desired_direction = [0, 0]
        self.change_countdown = 0
        self.last_desired_speed = 1
        self.health_total = self.health
        self.cooldown = 0
        self.facing = [None, Direction.NORTH]
        self.hitbox = None
        self.visible_ = False
    def be_attacked(self, other):
        """Be attacked by another creature"""
        self.health -= other.strength
    def dead(self):
        return self.health <= 0
    def death(self):
        """Deals with the eventual death of the creature"""
        if self.dead():
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
    def visible(self, obj):
        """Return true if obj is visible to self"""
        return self.within_distance(obj, self.light_radius)
    def target_visible(self):
        return self.visible(self.target)
    def roam(self):
        """Move randomly"""
        x, y = self.x, self.y
        self.change_countdown -= 1
        if (not self.continue_last_desired()
            and from_probability_to_bool(ROAM_RATE)):
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
    def draw(self):
        if self.visible_:
            super(Creature, self).draw()
