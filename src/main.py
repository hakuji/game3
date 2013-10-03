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

import pyglet
from control import state
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_NAME, INTERVAL
from util import KeySubscription, Option, SubscriptionFound
from pyglet.window import key
from pyglet import gl
from menu import MAIN_MENU, VICTORY_SCREEN, DEFEAT_SCREEN

window = pyglet.window.Window(
    caption = GAME_NAME,
    width = WINDOW_WIDTH,
    height = WINDOW_HEIGHT)

@window.event
def on_key_press(symbol, modifiers):
    try:
        state.react(symbol, modifiers)
    except SubscriptionFound:
        pass

@window.event
def on_draw():
    window.clear()
    state.draw()

def init():
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_BLEND)
    gl.glClearColor(0.0,0.0,0.0,0.0)
    state.subs.extend([
        KeySubscription(state.back_one_screen, key.Q),
        KeySubscription(state.back_one_screen, key.ESCAPE),
        KeySubscription(state.quit, key.C, key.MOD_CTRL)
    ])
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    state.khandler = keys
    state.screens.append(MAIN_MENU)
    state.victory = VICTORY_SCREEN
    state.defeat = DEFEAT_SCREEN
    MAIN_MENU.contents.append(Option(
        state.subs[0:1],
        'Quit',
        pyglet.text.Label(
            font_name='Times',
            font_size=12,
            x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 92,
            anchor_x='center', anchor_y='center')))
    pyglet.clock.schedule_interval(state.update, INTERVAL)
    pyglet.app.run()

if __name__ == '__main__':
    init()
