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
from util import Container, KeySubscription, Reactable
from constants import (
    STATS_PANEL_X,
    STATS_PANEL_Y,
    FIELD_FONT_SIZE,
    FADEOUT_STEP,
    TEXT_X,
    TEXT_Y,
    TEXT_WIDTH,
    TEXT_HEIGHT,
    TEXT_COLOR,
    TEXT_FONT,
    TEXT_SIZE,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    Controls,
    DEBUG,
    STATUS_PANEL_HEIGHT)
from function import fadeout, vertex_list_from_rect
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
            if self.ex is None:
                self.fade = 0
                self.ex = ex

class LabeledField(Container):
    def __init__(self, label, value_func, x, y):
        self.label = pyglet.text.Label(
            label + ':',
            font_name=TEXT_FONT,
            font_size=FIELD_FONT_SIZE,
            x=x, y=y)
        self.value = pyglet.text.Label(
            font_name=TEXT_FONT,
            font_size=FIELD_FONT_SIZE,
            x = x + self.label.content_width + 15,
            y = y)
        self.value_func = value_func
        self.contents = [self.label, self.value]
    def draw(self):
        self.value.text = str(self.value_func())
        super(LabeledField, self).draw()

class HealthBar(LabeledField):
    def __init__(self, hero, x, y):
        hfunc = lambda : hero.health
        super(HealthBar, self).__init__('Health', hfunc, x, y)
        self.hero = hero
    def draw(self):
        proportion = float(self.hero.health) / self.hero.health_total
        color = (int((1.0 - proportion) * 255), int(proportion * 255), 0, 255)
        width = int(HEALTH_BAR_WIDTH * proportion)
        bar = vertex_list_from_rect(
            self.value.x,
            self.value.y - 3,
            width,
            HEALTH_BAR_HEIGHT,
            color)
        bar.draw(pyglet.gl.GL_QUAD_STRIP)
        super(HealthBar, self).draw()

class MessageLog(object):
    def __init__(self):
        self.document = pyglet.text.decode_attributed(' ')
        self.document.set_style(
            0,
            32000000,
            {
                'color' : TEXT_COLOR,
                'font_name' : TEXT_FONT,
                'font_size' : TEXT_SIZE
            })
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, TEXT_WIDTH, TEXT_HEIGHT, True)
        self.layout.x = TEXT_X
        self.layout.y = TEXT_Y
        self.document.insert_text(1, '\n')
    def append_message(self, msg):
        msg = msg[0].upper() + msg[1:]
        if msg[-1] not in ".?!":
            msg += '.\n'
        else:
            msg += '\n'
        self.document.insert_text(len(self.document.text), msg)
        self.display_line = self.layout.get_line_count() - 2
        self.layout.ensure_line_visible(-1)
    def append_formated(self, msg):
        idx = len(self.document.text) + msg.index()
        self.append_message(str(msg))
        self.document.set_style(idx, idx + 1, {'color' : msg.obj.sprite.color})
    def append_messages(self, msgs):
        for m in msgs:
            if type(m) == str:
                self.append_message(m)
            else:
                self.append_formated(m)
    def page_up(self):
        self.display_line = max(0, self.display_line - 5)
        self.layout.ensure_line_visible(self.display_line)
    def page_down(self):
        self.display_line = min(self.layout.get_line_count() - 1,
                                self.display_line + 5)
        self.layout.ensure_line_visible(self.display_line)
    def draw(self):
        self.layout.draw()

class CommonScreen(Screen, Reactable):
    def __init__(self, state):
        self.state = state
        hfield = HealthBar(state.hero, STATS_PANEL_X, STATS_PANEL_Y)
        def pfunc():
            return str(self.state.level_no)
        pfield = LabeledField('Level', pfunc, STATS_PANEL_X, STATS_PANEL_Y - 30)
        self.message_log = MessageLog()
        self.contents = [hfield, pfield, self.message_log]
        self.level = state.level
        self.fade = 255
        self.step = FADEOUT_STEP
        self.subs = [
            KeySubscription(self.message_log.page_up, Controls.SCROLL_UP),
            KeySubscription(self.message_log.page_down, Controls.SCROLL_DOWN)]
    def react(self, key, modifiers):
        super(CommonScreen, self).react(key, modifiers)
        Reactable.react(self, key, modifiers)
    def update(self):
        self.fade = max(self.fade - self.step, 0)
        if self.fade < 50:
            self.state.update()
            self.message_log.append_messages(self.state.messages)
            self.message_log.append_messages(self.level.messages)
            self.state.messages = []
            self.level.messages = []
    def draw(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(0.0, STATUS_PANEL_HEIGHT, 0.0)
        self.level.draw()
        pyglet.gl.glPopMatrix()
        if not DEBUG:
            super(CommonScreen, self).draw()
            if self.fade > 0:
                fadeout(self.fade)
