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
from util import Reactable, Hero, Stage
from screens import CommonScreen
from stage_objects import STAGES

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
    def get_chsc_callback(self, screen):
        """Return a function that changes the current screen"""
        return lambda : self.screens.append(screen)
    def start_game(self, dificulty, hero = None, stage_no = 0):
        """Where the magic starts"""
        if hero is None:
            hero = Hero(self.khandler)
        self.game_state = GameState(dificulty, hero, stage_no)
        self.screens.append(CommonScreen(self.game_state))
    def back_one_screen(self):
        """Revert to previous screen or quit"""
        if len(self.screens) > 1:
            self.screens.pop()
        else:
            self.quit()
    def quit(self):
        """Politely exit the game"""
        pyglet.app.exit()
    def draw(self):
        """Draws the current screen"""
        self.top_screen().draw()
    def update(self, dt):
        """Update the game"""
        pass
    def react(self, key, modifiers):
        """Calls default reactions and screen specific reactions to keyboard
events"""
        super(GameController, self).react(key, modifiers)
        self.top_screen().react(key, modifiers)

class GameState(object):
    """State of the playable parts of the game"""
    def __init__(self, dificulty, hero, stage_no):
        self.dificulty = dificulty
        self.hero = hero
        self.stage_no = stage_no
        self.stage = Stage(STAGES[stage_no], [], [hero])

state = GameController()
