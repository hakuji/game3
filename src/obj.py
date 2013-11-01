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

import pyglet, types
from util import Drawable
from rect import Point, Rect
from constants import (
    OBJECT_FONT_SIZE,
    OBJECT_FONT_FACE,
    DEBUG,
    TEXT_COLOR)
from decorations import autoset
from function import vertex_list_from_rect

def empty_interaction(self):
    pass

class Object(Drawable):
    """An object in game"""
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
                 event_map = {}, range = 1, id = None, x = 0,
                 y = 0, color = TEXT_COLOR):
        self._set_properties(go_through, symbol, description, range,
                             id)
        sprite = pyglet.text.Label(
            symbol,
            font_name=OBJECT_FONT_FACE,
            font_size=OBJECT_FONT_SIZE, color=color)
        self.set_events(event_map)
        super(Object, self).__init__(sprite)
        self.x = x
        self.y = y
        self.rect_ = Rect.from_dimensions(0, 0, self.w, self.h)
    def get_default_map(self):
        return {'on_interact': empty_interaction}
    def set_events(self, event_map):
        nm = self.get_default_map()
        nm.update(event_map)
        for k in nm:
             self.__setattr__(k, types.MethodType(nm[k], self))
    @autoset
    def _set_properties(self, go_through, symbol, description,
                 range, id):
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
        if DEBUG:
            x, y = self.x, self.y
            w, h = self.w, self.h
            rect = vertex_list_from_rect(x, y, w, h)
            rect.draw(pyglet.gl.GL_QUAD_STRIP)
        super(Object, self).draw()
    def __str__(self):
        return self.description + '({0})'.format(self.symbol)
