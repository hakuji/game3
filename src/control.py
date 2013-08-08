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
from util import Reactable
from screens import first_stage

class GameController(Reactable):
    """Ui controller"""
    def __init__(self, main_menu = None, subs = None):
        if main_menu is None:
            main_menu = []
        if subs is None:
            subs = []
        self.screens = main_menu
        self.subs = subs
    def top_screen(self):
        return self.screens[-1]
    def start_game(self, game_state = None):
        """Where the magic happens"""
        if game_state is None:
            game_state = GameState(self.get_hero())
        self.game_state = game_state
    def get_hero(self):
        """Return a hero set by the hero selection screen"""
        return None
    def back_one_screen(self):
        """Revert to previous screen or quit"""
        if len(self.screens) > 1:
            self.screens.pop()
        else:
            pyglet.app.exit()
    def draw(self):
        """Draws the current screen"""
        self.top_screen().draw()
    def react(self, key, modifiers):
        """Calls default reactions and screen specific reactions"""
        super(GameController, self).react(key, modifiers)
        self.top_screen().react(key, modifiers)

class GameState(object):
    """State of the playable parts of the game"""
    def __init__(self, hero, stage = first_stage):
        pass
state = GameController()
