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

window = pyglet.window.Window(
    caption = GAME_NAME,
    width = WINDOW_WIDTH,
    height = WINDOW_HEIGHT)


hero = Hero(None)
state = CommonScreen(GameState(False, hero, 0))

@window.event
def on_key_release(symbol, modifiers):
    if key.Q == symbol:
        pyglet.app.exit()
    if key.R == symbol:
        import stage_objects
        state.level = stage_objects.LEVELS[0](hero)

@window.event
def on_draw():
    window.clear()
    state.draw()

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
