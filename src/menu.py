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

"""List of game menus"""
import pyglet
from util import KeySubscription, Screen, Option
from pyglet.window import key
from constants import (WINDOW_WIDTH, WINDOW_HEIGHT, NORMAL_DIFICULTY, GAME_NAME,
                       VICTORY, GAME_OVER)
from control import state

def get_start(dificulty):
    def l():
        state.start_game(dificulty)
        del state.screens[-2]
    return l

CHOOSE_DIFICULTY = Screen([
    pyglet.text.Label('Choose the game dificulty',
                          font_name='Times',
                          font_size=25,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                          anchor_x='center', anchor_y='center'),
    Option([KeySubscription(get_start(NORMAL_DIFICULTY), key.N)],
           'Normal',
           pyglet.text.Label(font_name='Times',
                          font_size=12,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 52,
                          anchor_x='center', anchor_y='center')),
    Option([KeySubscription(get_start(not NORMAL_DIFICULTY), key.H)],
           'Hard',
           pyglet.text.Label(font_name='Times',
                          font_size=12,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 72,
                          anchor_x='center', anchor_y='center'))
])

MAIN_MENU = Screen([
    pyglet.text.Label(GAME_NAME,
                          font_name='Times',
                          font_size=36,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                          anchor_x='center', anchor_y='center'),
    Option([KeySubscription(
        state.get_chsc_callback(CHOOSE_DIFICULTY), key.N)],
           'New game',
           pyglet.text.Label(font_name='Times',
                          font_size=12,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 72,
                          anchor_x='center', anchor_y='center'))
])

VICTORY_SCREEN = Screen([
    pyglet.text.Label(VICTORY,
                          font_name='Times',
                          font_size=36,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                          anchor_x='center', anchor_y='center')
])

DEFEAT_SCREEN = Screen([
    pyglet.text.Label(GAME_OVER,
                          font_name='Times',
                          font_size=36,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                          anchor_x='center', anchor_y='center')
])
