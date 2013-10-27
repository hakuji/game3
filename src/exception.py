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

"""Game exceptions"""

from decorations import autoset

class StartGame(Exception):
    @autoset
    def __init__(self, dificulty):
        pass

class BackOneScreen(Exception):
    pass

class QuitGame(Exception):
    pass

class Fadeout(Exception):
    @autoset
    def __init__(self, step):
        pass

class SubscriptionFound(Exception):
    pass

class NextLevel(Exception):
    pass

class PreviousLevel(Exception):
    pass

class CreatureDeath(Exception):
    pass

class GameOver(Exception):
    @autoset
    def __init__(self, defeat):
        pass

class ImpossiblePathwayException(Exception):
    pass

class ReplaceObject(Exception):
    @autoset
    def __init__(self, this, that):
        pass

class CreateObject(Exception):
    @autoset
    def __init__(self, obj):
        pass

class AnimationEnd(Exception):
    pass

class AppendMessage(Exception):
    pass

class EventList(Exception):
    """An event that has a list of events"""
    @autoset
    def __init__(self, events):
        pass
