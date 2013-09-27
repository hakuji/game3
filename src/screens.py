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

from util import Container
from constants import STATS_PANEL_X, STATS_PANEL_Y, FIELD_FONT_SIZE
import pyglet

class Screen(Container):
    def react(self, key, modifiers):
        for i in self.contents:
            try:
                i.react(key, modifiers)
            except AttributeError:
                pass

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
