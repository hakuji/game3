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

import pyglet, sys
from util import Container
from constants import (
    STATS_PANEL_X,
    STATS_PANEL_Y,
    FIELD_FONT_SIZE,
    FADEOUT_STEP,
    TEXT_X,
    TEXT_Y,
    TEXT_WIDTH,
    TEXT_HEIGHT)
from function import fadeout
from exception import StartGame

class Screen(Container):
    def react(self, key, modifiers):
        for i in self.contents:
            if hasattr(i, 'react'):
                i.react(key, modifiers)

class MenuScreen(Screen):
    def __init__(self, contents):
        super(MenuScreen, self).__init__(contents)
        self.fade = 255
        self.ex = None
        self.fstep = FADEOUT_STEP
    def fade(self, next_screen):
        self.fade = 0
    def update(self):
        super(MenuScreen, self).update()
        self.fade = min(self.fade + self.fstep, 255)
        if self.ex is not None and self.fade == 255:
            ex = self.ex
            self.ex = None
            raise ex
    def draw(self):
        super(MenuScreen, self).draw()
        if self.fade < 255:
            fadeout(self.fade)
    def react(self, key, modifiers):
        try:
            super(MenuScreen, self).react(key, modifiers)
        except StartGame as ex:
            self.fade = 0
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
        document = pyglet.text.decode_html("<p>Top kek</p>")
        document.set_style(0, sys.maxint, dict(color=(255, 255, 255, 255)))
        self.message_log = pyglet.text.layout.IncrementalTextLayout(
            document,
            TEXT_WIDTH,
            TEXT_HEIGHT,
            True)
        self.message_log.x = TEXT_X
        self.message_log.y = TEXT_Y
        self.contents = [hfield, pfield,
                         state.level, self.message_log]
        self.fade = 255
        self.step = FADEOUT_STEP
    def update(self):
        self.fade = max(self.fade - self.step, 0)
        if self.fade < 50:
            self.state.update()
    def draw(self):
        super(CommonScreen, self).draw()
        if self.fade > 0:
            fadeout(self.fade)
