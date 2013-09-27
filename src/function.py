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

"""Utility functions"""

import pyglet

ran = range
def range(*args):
    """Beefed out version of range that automatically deals
    with reverse direction

    range([start,] stop[, step]) -> list of integers

    Return a list containing an arithmetic progression of integers.
    range(i, j) returns [i, i+1, i+2, ..., j-1]; start (!) defaults to 0.
    When step is given, it specifies the increment (or decrement).
    For example, range(4) returns [0, 1, 2, 3].  The end point is omitted!
    These are exactly the valid indices for a list of 4 elements."""
    if len(args) == 3:
        return ran(*args)
    elif len(args) == 2:
        if args[0] <= args[1]:
            return ran(args[0], args[1])
        else:
            return ran(args[0] - 1, args[1] - 1, -1)
    elif len(args) == 1:
        return ran(args[0])
    elif len(args) == 0:
        raise TypeError('range takes at least 1 argument (0 given)')
    else:
        raise TypeError('range takes at most 3 arguments (0 given)'.format([str(len(args))]))

def range_inc(*args):
    """Like range but inclusive"""
    if len(args) == 3:
        if args[0] <= args[1]:
            return ran(args[0], args[1] + 1, args[2])
        else:
            return ran(args[0], args[1] - 1, args[2])
    elif len(args) == 2:
        if args[0] <= args[1]:
            return ran(args[0], args[1] + 1)
        else:
            return ran(args[0], args[1] - 1, -1)
    elif len(args) == 1:
        return ran(args[0] + 1)
    elif len(args) == 0:
        raise TypeError('range takes at least 1 argument (0 given)')
    else:
        raise TypeError('range takes at most 3 arguments (0 given)'.format([str(len(args))]))

def vertex_list_from_rect(x, y, w, h, color = (0, 0, 255)):
    r, g, b = color
    return pyglet.graphics.vertex_list(
        4, ('v2i', (x,     y,
                    x + w, y,
                    x,     y + h,
                    x + w, y + h)),
        ('c3B', (r, g, b,
                 r, g, b,
                 r, g, b,
                 r, g, b)
        ))

