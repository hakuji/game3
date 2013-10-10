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
from util import Container
from constants import STATS_PANEL_X, STATS_PANEL_Y, FIELD_FONT_SIZE
from function import fadeout
from exception import StartGame

class Screen(Container):
    def __init__(self, contents):
        super(Screen, self).__init__(contents)
        self.fadeout = 255
        self.ex = None
        self.fstep = 20
    def fadeout(self, next_screen):
        self.fadeout = 0
    def update(self):
        super(Screen, self).update()
        self.fadeout = min(self.fadeout + self.fstep, 255)
        if self.ex is not None and self.fadeout == 255:
            ex = self.ex
            self.ex = None
            raise ex
    def draw(self):
        super(Screen, self).draw()
        if self.fadeout < 255:
            fadeout(self.fadeout)
    def react(self, key, modifiers):
        try:
            for i in self.contents:
                if hasattr(i, 'react'):
                    i.react(key, modifiers)
        except StartGame as ex:
            self.fstep = 20
            self.fadeout = 0
            self.ex = ex

class LabeledField(Container):
    def __init__(self, label, value_func, x, y):
        self.label = pyglet.text.Label(
            label + ':',
            font_name='Times',
            font_size=FIELD_FONT_SIZE,
            x=x, y=y)
        self.value = pyglet.text.Label(
            font_name='Times',
            font_size=FIELD_FONT_SIZE,
            x = x + self.label.content_width + 15,
            y = y)
        self.value_func = value_func
        self.contents = [self.label, self.value]
    def draw(self):
        self.value.text = str(self.value_func())
        super(LabeledField, self).draw()

class CommonScreen(Screen):
    def __init__(self, state):
        self.state = state
        hfunc = lambda : self.state.hero.health
        hfield = LabeledField('Health', hfunc, STATS_PANEL_X, STATS_PANEL_Y)
        def pfunc():
            return str(self.state.level_no)
        pfield = LabeledField('Level', pfunc, STATS_PANEL_X, STATS_PANEL_Y - 30)
        self.contents = [hfield, pfield,
                         state.level]#message_box
    def update(self):
        self.state.update()
