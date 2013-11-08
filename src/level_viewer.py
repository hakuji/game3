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
                       BACKGROUND_COLOR, STATUS_PANEL_HEIGHT, Color)
constants.DEBUG = True
from control import GameState
from pyglet.window import key
from screens import CommonScreen
from pyglet import gl
from hero import Hero
from room import Room
from obj import Object

window = pyglet.window.Window(
    caption = GAME_NAME,
    width = WINDOW_WIDTH,
    height = WINDOW_HEIGHT)

NEW_ROOM = 1
NEW_LEVEL = 2
MOVE_PROP = 3
DEFAULT_STATE = MOVE_PROP
STATUS_PANEL_HEIGHT = int(STATUS_PANEL_HEIGHT)
SELECTION_COLOR = (155, 155, 155, 255)

hero = Hero(None)
state = CommonScreen(GameState(False, hero, 0))
xy0 = None
vl = pyglet.graphics.vertex_list(
        6, ('v2i', (0, 0) * 6 ),
        ('c4B', SELECTION_COLOR * 6))
new_level = False
buff = ""
m = __import__('level1' + buff)
ui_state = None
prop = Object(False, 'T', 'Prop')
state.level.objects.append(prop)
label = pyglet.text.Label("", color=Color.WHITE, x=20, y=20)

def change_state(state):
    global ui_state
    ui_state = state
    if ui_state == NEW_ROOM:
        label.text = "Place new room"
    if ui_state == NEW_LEVEL:
        label.text = "Type new level number and press enter"
    if ui_state == MOVE_PROP:
        label.text = "Click to move test prop"

change_state(DEFAULT_STATE)

def delta_xy(x, y):
    x0 = min(x, xy0[0])
    y0 = min(y, xy0[1])
    x1 = max(x, xy0[0])
    y1 = max(y, xy0[1])
    dx = x1 - x0
    dy = y1 - y0
    return (x0, y0, dx - 20, dy - 20)

def reload_stage():
    import stage_objects
    try:
        reload(stage_objects)
        reload(m)
    except Exception as ex:
        print(ex)
    state.level = m.LEVEL(hero)
    state.level.objects.append(prop)

@window.event
def on_key_release(symbol, modifiers):
    global new_level, buff, m, ui_state
    if key.Q == symbol:
        pyglet.app.exit()
    elif key.R == symbol:
        reload_stage()
    elif key.N == symbol:
        change_state(NEW_LEVEL)
        buff = ""
    elif key.O == symbol:
        change_state(NEW_ROOM)
    elif key.M == symbol:
        change_state(MOVE_PROP)
    elif key.ENTER == symbol:
        change_state(DEFAULT_STATE)
        if buff != "":
            try:
                m = __import__('level' + buff)
                reload_stage()
                print 'level' + buff + ' loaded'
            except ImportError as err:
                print err
    else:
        if ui_state == NEW_LEVEL:
            n = processNumber(symbol)
            if n is not None:
                buff += n

def processNumber(symbol):
    for i in range(0, 10):
        i = str(i)
        if symbol == getattr(key, '_' + i):
            return i
    return None

@window.event
def on_mouse_release(x, y, button, modifiers):
    y -= STATUS_PANEL_HEIGHT
    if xy0 != (x, y) and ui_state == NEW_ROOM:
        dxy = delta_xy(x, y)
        room = Room(dxy[0], dxy[1], dxy[2], dxy[3])
        state.level.rooms.append(room)
        vl.colors[:] = BACKGROUND_COLOR * 6
        print('Room{0}'.format(str(dxy)))
    elif ui_state == MOVE_PROP:
        prop.x = x
        prop.y = y
        print (x, y)

@window.event
def on_mouse_press(x, y, button, modifiers):
    y -= STATUS_PANEL_HEIGHT
    global xy0
    xy0 = (x, y)
    vl.vertices[:] = [x, y + STATUS_PANEL_HEIGHT] * 6
    vl.colors[:] = SELECTION_COLOR * 6


@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    oldx = vl.vertices[-2]
    oldy = vl.vertices[-1]
    newx = oldx + dx
    newy = oldy + dy
    vl.vertices[:] = [xy0[0], xy0[1] + STATUS_PANEL_HEIGHT,
                      xy0[0], xy0[1] + STATUS_PANEL_HEIGHT,
                      newx  , xy0[1] + STATUS_PANEL_HEIGHT,
                      xy0[0], newy,
                      newx,   newy,
                      newx,   newy
]

@window.event
def on_draw():
    window.clear()
    state.draw()
    vl.draw(gl.GL_QUAD_STRIP)
    label.draw()

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
