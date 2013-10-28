#!/bin/python
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

import pyglet, constants
from constants import (WINDOW_WIDTH, WINDOW_HEIGHT, GAME_NAME,
                       BACKGROUND_COLOR)
constants.DEBUG = True
from control import GameState
from pyglet.window import key
from screens import CommonScreen
from pyglet import gl
from hero import Hero
from function import vertex_list_from_rect

window = pyglet.window.Window(
    caption = GAME_NAME,
    width = WINDOW_WIDTH,
    height = WINDOW_HEIGHT)


hero = Hero(None)
state = CommonScreen(GameState(False, hero, 0))
xy0 = None
vl = vertex_list_from_rect(0, 0, 0, 0, (155, 155, 155, 255))

def delta_xy(x, y):
    x0 = min(x, xy0[0])
    y0 = min(y, xy0[1])
    x1 = max(x, xy0[0])
    y1 = max(y, xy0[1])
    dx = x1 - x0
    dy = y1 - y0
    return (x0, y0, dx, dy)

@window.event
def on_key_release(symbol, modifiers):
    if key.Q == symbol:
        pyglet.app.exit()
    if key.R == symbol:
        import stage_objects
        reload(stage_objects)
        state.level = stage_objects.LEVELS[0](hero)

@window.event
def on_mouse_release(x, y, button, modifiers):
    if xy0 != (x, y):
        print(delta_xy(x, y))
    else:
        print(x, y)

@window.event
def on_mouse_press(x, y, button, modifiers):
    global xy0
    xy0 = (x, y)

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    dxy = (x - xy0[0], y - xy0[1])
    vl.vertices[:] = [xy0[0], xy0[1],
                      xy0[0] + dxy[0], xy0[1],
                      xy0[0], xy0[1] + dxy[1],
                      xy0[0] + dxy[0], xy0[1] + dxy[1]]

@window.event
def on_draw():
    window.clear()
    state.draw()
    vl.draw(gl.GL_QUAD_STRIP)

def init():
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_BLEND)
    gl.glClearColor(*BACKGROUND_COLOR)
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    state.khandler = keys
    pyglet.app.run()

if __name__ == '__main__':
    init()
