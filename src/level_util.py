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

from exception import AppendMessage, PreviousLevel
from functools import partial
from function import raise_ev
from obj import Object

def on_interact_map(fun):
    return {'on_interact': fun}

append_message = partial(raise_ev, AppendMessage)

def on_interact_append_message(message):
    return on_interact_map(append_message(message))

ASC_STAIRS = partial(
    Object,
    True,
    '<',
    'ascending stairs',
    event_map = on_interact_map(raise_ev(PreviousLevel)),
    id = -2,
)
