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

import pyglet, math
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, DEBUG

def get_tile(x, y, tile_size, group, batch):
    vl = batch.add(
        6, pyglet.gl.GL_QUAD_STRIP, group,
        ('v2i', (x, y, x, y,
                 x + tile_size, y,
                 x, y + tile_size,
                 x + tile_size, y + tile_size,
                 x + tile_size, y + tile_size
             ))
    )
    vl.x = x
    vl.y = y
    vl.explored = 0
    return vl

class FogGroup(pyglet.graphics.Group):
    def __init__(self,  alpha):
        self.alpha = alpha
        super(FogGroup, self).__init__()
    def set_state(self):
        pyglet.gl.glColor4ub(0, 0, 0, self.alpha)
    def unset_state(self):
        pyglet.gl.glColor4ub(0, 0, 0, 0)

x = 0
y = 50
w = WINDOW_WIDTH - x
h = WINDOW_HEIGHT - y
unexplored_group = FogGroup(255)
explored_group = FogGroup(100)
visible_group = FogGroup(0)
batch = pyglet.graphics.Batch()
tile_size = 5
matrix = [[get_tile(j, i, tile_size, unexplored_group, batch)
                for j in range(x, w, tile_size)]
               for i in range(y, h, tile_size)]

def draw_fog():
    batch.draw()

def tile_visible_from(x, y, light_radius, tile):
    x1 = tile.vertices[0]
    y1 = tile.vertices[1]
    return math.hypot(x - x1, y - y1) <= light_radius

def update_fog(x, y, light_radius):
    margin = 10
    i1 = (x / tile_size) - (light_radius / tile_size) - margin
    j1 = (y / tile_size) - (light_radius / tile_size) - margin
    i1 = max(i1, 0)
    j1 = max(j1, 0)
    i2 = i1 + 15 + margin
    j2 = j1 + 5 + margin
    i2 = min(i2, len(matrix[0]))
    j2 = min(j2, len(matrix))
    for i in range(i1, i2):
        for j in range(j1, j2):
            t = matrix[j][i]
            if tile_visible_from(x, y, light_radius, t):
                batch.migrate(t, pyglet.gl.GL_QUAD_STRIP, visible_group, batch)
                t.explored = 1
            elif t.explored == 1:
                batch.migrate(t, pyglet.gl.GL_QUAD_STRIP, explored_group, batch)
                t.explored = 2
