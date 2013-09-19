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

from util import Screen, Container, LabeledField
from constants import STATS_PANEL_X

def health():
    return 10

def place():
    return 'Nowhere'

STATS_PANEL = Container([
    LabeledField('Health', health, STATS_PANEL_X, 460),
    LabeledField('Place', place, STATS_PANEL_X, 430)
])

class CommonScreen(Screen):
    def __init__(self, state):
        self.state = state
        self.contents = [STATS_PANEL,
                         state.stage]#message_box, tool_panel])
    def update(self):
        self.state.update()
