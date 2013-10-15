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

from pyglet.window import key

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FIELD_FONT_SIZE = 12
OBJECT_FONT_SIZE = 10
STATS_PANEL_X = 520
STATS_PANEL_Y = 70
ST_BOUND_X = 480
ST_BOUND_Y = 470
WALL_WIDTH = 10
NORMAL_DIFICULTY = True
GAME_NAME = 'GAME 3'
OBJECT_FONT_FACE = 'Monospace'
INTERVAL = 0.1
VICTORY = 'YOU WIN!'
GAME_OVER = 'GAME OVER'
ROAM_LIST = [-1, 0, 0, 0, 1]
HITBOX_GAP = 3
INTERACT_COOLDOWN = 10
BACKGROUND_COLOR = [0, 0, 0, 0]
class Direction(object):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'
ACCEPT_KEY = key.I
ROOM_FLOOR_COLOR = (150, 50, 255, 255)
FADEOUT_STEP = 30
HERO_ID = -1
TEXT_WIDTH = 400
TEXT_HEIGHT = 5 * 24
TEXT_X = 30
TEXT_Y = -10
TEXT_COLOR = (255, 255, 255, 255)
TEXT_FONT = 'Times'
TEXT_SIZE = 12
FIRST_MESSAGE = 'Press ? for help with the controls'
