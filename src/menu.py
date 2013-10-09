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
from util import KeySubscription, Drawable, Reactable
from screens import Screen
from decorations import autoset
from pyglet.window import key
from constants import (WINDOW_WIDTH, WINDOW_HEIGHT, NORMAL_DIFICULTY, GAME_NAME,
                       VICTORY, GAME_OVER, ACCEPT_KEY)
from exception import StartGame

class Option(Drawable, Reactable):
    """Option accessed with a key"""
    @autoset
    def __init__(self, subs, description, sprite):
        self.sprite.text = self.get_text()
    def keypart(self):
        keystr = [str(i) for i in self.subs]
        if len(keystr) > 1:
            return ', '.join(keystr[:-1]) + ' or ' + keystr[-1]
        else:
            return keystr[0]
    def get_text(self):
        return self.keypart() + ' - ' + self.description

def start_game(dificulty):
    def f(): 
        raise StartGame(dificulty)
    return f

CHOOSE_DIFICULTY = Screen([
    pyglet.text.Label('Choose the game dificulty',
                          font_name='Times',
                          font_size=25,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                          anchor_x='center', anchor_y='center'),
    Option([KeySubscription(start_game(NORMAL_DIFICULTY), key.N)],
           'Normal',
           pyglet.text.Label(font_name='Times',
                          font_size=12,
                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2 - 52,
                          anchor_x='center', anchor_y='center')),
    Option([KeySubscription(start_game(not NORMAL_DIFICULTY), key.H)],
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
    Option([KeySubscription(start_game(NORMAL_DIFICULTY), ACCEPT_KEY)],
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
