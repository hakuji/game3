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

class SubscriptionFound(Exception):
    pass

class UnplaceableRoomException(Exception):
    pass

class NextLevelException(Exception):
    pass

class CreatureDeathException(Exception):
    pass

class GameOverException(Exception):
    def __init__(self, defeat):
        self.defeat = defeat

class ImpossiblePathwayException(Exception):
    pass

class ReplaceObjectException(Exception):
    def __init__(self, this, that):
        self.this = this
        self.that = that

class AnimationEnd(Exception):
    pass
