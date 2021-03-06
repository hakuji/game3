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

import pyglet, pickle, cloud
from util import Reactable
from hero import Hero
from exception import (
    NextLevel,
    GameOver,
    PreviousLevel,
    StartGame,
    BackOneScreen,
    QuitGame,
    AutoSave)
from screens import CommonScreen
from stage_objects import LEVELS
from constants import INTERVAL
from decorations import autoset
from menu import QUIT_SUBSCRIPTIONS, VICTORY_SCREEN, DEFEAT_SCREEN, MAIN_MENU

class GameController(Reactable):
    """Ui controller"""
    def __init__(self):
        self.victory = VICTORY_SCREEN
        self.defeat = DEFEAT_SCREEN
        self.screens = [MAIN_MENU]
        self.subs = QUIT_SUBSCRIPTIONS
    def top_screen(self):
        return self.screens[-1]
    def add_screen(self, screen):
        """Changes the current screen"""
        self.screens.append(screen)
    def start_game(self, dificulty, hero = None):
        """Where the magic starts"""
        if hero is None:
            hero = Hero(self.khandler)
        self.game_state = GameState(dificulty, hero)
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
    def save(self):
        with open('save_file.bin', 'wb') as fil:
            self.game_state.get_level().unset_visual()
            cloud.serialization.cloudpickle.dump(self.game_state, fil)
            self.game_state.get_level().set_visual()
    def update(self, dt):
        """Update the game"""
        try:
            for i in range(int(dt // INTERVAL)):
                self.top_screen().update()
        except GameOver as ex:
            self.back_one_screen()
            if ex.defeat:
                self.add_screen(self.defeat)
            else:
                self.add_screen(self.victory)
        except StartGame as ex:
            self.start_game(ex.dificulty)
        except AutoSave:
            self.save()
    def react(self, key, modifiers):
        """Calls default reactions and screen specific reactions to keyboard
events"""
        try:
            super(GameController, self).react(key, modifiers)
            self.top_screen().react(key, modifiers)
        except QuitGame:
            self.quit()
        except BackOneScreen:
            self.back_one_screen()

class GameState(object):
    """State of the playable parts of the game"""
    @autoset
    def __init__(self, dificulty, hero, current_level=0,
                 levels = None):
        if levels is None:
            self.levels = [LEVELS[current_level](hero)]
        self.messages = []
    def goto_next_level(self):
        """Move to the next level or end the game"""
        self.get_level().unset_visual()
        self.current_level += 1
        try:
            level = LEVELS[self.current_level]
        except IndexError:
            raise GameOver(False)
        self.levels.append(level(self.hero))
    def goto_prev_level(self):
        """Move to the previous level"""
        self.current_level -= 1
        self.get_level().set_visual()
    def get_level(self):
        return self.levels[self.current_level]
    def update(self):
        try:
            self.get_level().update()
        except NextLevel:
            self.goto_next_level()
            raise AutoSave()
        except PreviousLevel:
            self.goto_prev_level()

state = GameController()
