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
from util import Reactable, Hero
from exception import (NextLevelException, GameOverException,
                       PreviousLevelException)
from screens import CommonScreen
from stage_objects import LEVELS
from constants import INTERVAL
from decorations import autoset

class GameController(Reactable):
    """Ui controller"""
    def __init__(self, main_menu = None, subs = None):
        if main_menu is None:
            main_menu = []
        if subs is None:
            subs = []
        self.victory = None
        self.defeat = None
        self.screens = main_menu
        self.subs = subs
    def top_screen(self):
        return self.screens[-1]
    def get_chsc_callback(self, screen):
        """Return a function that changes the current screen"""
        return lambda : self.add_screen(screen)
    def add_screen(self, screen):
        """Changes the current screen"""
#        fadeout()
        self.screens.append(screen)
    def start_game(self, dificulty, hero = None, stage_no = 0):
        """Where the magic starts"""
        if hero is None:
            hero = Hero(self.khandler)
        self.game_state = GameState(dificulty, hero, stage_no)
        self.add_screen(CommonScreen(self.game_state))
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
        try:
            for i in range(int(dt // INTERVAL)):
                self.top_screen().update()
        except GameOverException as ex:
            self.back_one_screen()
            if ex.defeat:
                self.add_screen(self.defeat)
            else:
                self.add_screen(self.victory)
    def react(self, key, modifiers):
        """Calls default reactions and screen specific reactions to keyboard
events"""
        super(GameController, self).react(key, modifiers)
        self.top_screen().react(key, modifiers)

class GameState(object):
    """State of the playable parts of the game"""
    @autoset
    def __init__(self, dificulty, hero, level_no):
        self.level = LEVELS[level_no](hero)
    def goto_next_level(self):
        """Move to the next level or end the game"""
        self.level_no += 1
        try:
            level = LEVELS[self.level_no]
        except IndexError:
            raise GameOverException(False)
        self.level = level(self.hero)
    def goto_prev_level(self):
        """Move to the previous level"""
        self.level_no -= 1
        self.level = LEVELS[self.level_no](self.hero)
    def update(self):
        try:
            self.level.update()
        except NextLevelException:
            self.goto_next_level()
        except PreviousLevelException:
            self.goto_prev_level()

state = GameController()
