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
from util import Screen, Container
from constants import STATS_PANEL_X, FIELD_FONT_SIZE as FONT_SIZE

class Stage(Screen):
    def __init__(self, contents, layout):
        self.layout = layout
        super(Stage, self).__init__(contents)

first_stage = Stage([], [])

class LabeledField(Container):
    def __init__(self, label, value_func, x, y):
        self.label = pyglet.text.Label(
            label + ':',
            font_name='Times',
            font_size=FONT_SIZE,
            x=x, y=y)
        self.value = pyglet.text.Label(
            font_name='Times',
            font_size=FONT_SIZE,
            x = x + self.label.content_width + 15,
            y = y)
        self.value_func = value_func
        self.contents = [self.label, self.value]

    def draw(self):
        self.value.text = str(self.value_func())
        super(LabeledField, self).draw()

def health():
    return 10

def place():
    return 'Nowhere'

STATS_PANEL = Container([
    LabeledField('Health', health, STATS_PANEL_X, 460),
    LabeledField('Place', place, STATS_PANEL_X, 430)
])



common_screen = Screen([STATS_PANEL])#stats_panel, message_box, tool_panel])
