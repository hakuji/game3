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
from decorations import autoset
from rect import Rect
from constants import WALL_WIDTH, ROOM_FLOOR_COLOR, Color
from function import vertex_list_from_rect
from random import randint
from exception import ImpossiblePathwayException

"""Room classes"""

class Room(object):
    @autoset
    def __init__(self, x, y, w, h, objects = [], creatures = [],
                 start  = False):
        self.inner_rect = Rect.from_dimensions(x + WALL_WIDTH, y + int(WALL_WIDTH * 1.25),
                                               w + WALL_WIDTH, h + int(WALL_WIDTH * 1.5))
        self.outer_rect = Rect.from_dimensions(x, y,
                                               2 * WALL_WIDTH + w,
                                               2 * WALL_WIDTH + h)
        self.set_visual()
    def draw(self):
        self.floor.draw(pyglet.gl.GL_QUAD_STRIP)
        for w in self.walls:
            w.draw(pyglet.gl.GL_QUAD_STRIP)
    def set_visual(self):
        """Method that sets the visual representation of an object"""
        self.walls = self.walls_from_rect(self.outer_rect)
        d = self.inner_rect.dimension()
        self.floor = vertex_list_from_rect(d[0], d[1] - 2, d[2], d[3], ROOM_FLOOR_COLOR)
    def unset_visual(self):
        """Method that unsets all references to the visual representation of an
        object"""
        del self.floor
        del self.walls
    @classmethod
    def walls_from_rect(cls, rect, color = Color.ARTICHOKE):
        x, y, w, h = rect.dimension()
        left = vertex_list_from_rect(x, y, WALL_WIDTH, WALL_WIDTH + h, color)
        top = vertex_list_from_rect(x, y + h, w, WALL_WIDTH, color)
        bottom = vertex_list_from_rect(x, y, w, WALL_WIDTH, color)
        right = vertex_list_from_rect(x + w, y, WALL_WIDTH, WALL_WIDTH + h, color)
        return (left, top, bottom, right)

class Pathway(Room):
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
        self.walls = self.walls_from_rect(self.outer_rect)
        self.set_visual()
    def draw(self):
        self.floor.draw(pyglet.gl.GL_QUAD_STRIP)
        self.awall.draw(pyglet.gl.GL_QUAD_STRIP)
        self.bwall.draw(pyglet.gl.GL_QUAD_STRIP)
    @classmethod
    def thickness(cls):
        return WALL_WIDTH * 3
    def set_visual(self):
        """Method that sets the visual representation of an object"""
        if self.horizontal:
            self.awall = self.walls[1]
            self.bwall = self.walls[2]
        else:
            self.awall = self.walls[0]
            self.bwall = self.walls[3]
        d = self.inner_rect.dimension()
        self.floor = vertex_list_from_rect(d[0], d[1], d[2], d[3], ROOM_FLOOR_COLOR)
    def unset_visual(self):
        """Method that unsets all references to the visual representation of an
        object"""
        del self.floor
        del self.awall
        del self.bwall
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
