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

import pyglet
from pyglet import gl
from creature import Creature
from decorations import autoset
from util import MeleeHitbox, Move
from constants import Direction, Controls, HERO_ID, Color
from exception import CreatureDeath, GameOver, AnimationEnd

class Hero(Creature):
    """Player controlable character"""
    @autoset
    def __init__(self, khandler, inv = None):
        super(Hero, self).__init__(
            symbol='@',
            description='You',
            health=100,
            speed=3,
            strength=3,
            light_radius=30,
            go_through=False,
            range=10,
            cooldown_=3,
            attack_type=MeleeHitbox,
            roaming=False,
            hostile=False,
            id=HERO_ID,
            color = Color.BLACK
        )
        self.speed = 3
        self.intended_interact = False
        self.animation = Move([Direction.EAST, None], 10, self)
        self.arrow = self.get_arrow()
        if inv is None:
            self.inv = []
        self.visible_ = True
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
        except CreatureDeath:
            raise GameOver(True)
        if self.animation is not None:
            try:
                self.animation.update()
            except AnimationEnd:
                self.animation = None
            return
        self.intended_interact = False
        facing = [None, None]
        if self.khandler[Controls.NORTH]:
            self.intended_y = self.y + self.speed
            facing[1] = Direction.NORTH
        if self.khandler[Controls.SOUTH]:
            self.intended_y = self.y - self.speed
            facing[1] = Direction.SOUTH
        if self.khandler[Controls.WEST]:
            self.intended_x = self.x - self.speed
            facing[0] = Direction.WEST
        if self.khandler[Controls.EAST]:
            self.intended_x = self.x + self.speed
            facing[0] = Direction.EAST
        if self.khandler[Controls.ACCEPT]:
            if self.cooldown == 0:
                self.intended_interact = True
                self.cooldown = self.cooldown_
            else:
                pass
        if facing != [None, None]:
            self.facing = facing
        if self.khandler[Controls.ATTACK]:
            self.attack()
    def set_animation(self, animation):
        self.animation = animation
