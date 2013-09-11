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

"""Point and Rectangle classes.

This code is an adaptation of http://wiki.python.org/moin/PointsAndRectangles

Point  -- point with (x,y) coordinates
Rect  -- two points, forming a rectangle
"""

import math

class Point(object):
    """A point identified by (x,y) coordinates.
    
    supports: +, -, *, /, str, repr
    
    length  -- calculate length of vector to point from origin
    distance_to  -- calculate distance between two points
    as_tuple  -- construct tuple (x,y)
    clone  -- construct a duplicate
    integerize  -- convert x & y to integers
    floatize  -- convert x & y to floats
    move_to  -- reset x & y
    slide  -- move (in place) +dx, +dy, as spec'd by point
    slide_xy  -- move (in place) +dx, +dy
    rotate  -- rotate around the origin
    rotate_about  -- rotate around another point
    """
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    def __add__(self, p):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x+p.x, self.y+p.y)
    def __sub__(self, p):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x-p.x, self.y-p.y)
    def __mul__( self, scalar ):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x*scalar, self.y*scalar)
    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x/scalar, self.y/scalar)
    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)
    def __repr__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__, self.x, self.y)
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()
    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)
    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)
    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)
    def tofloat(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)
    def toint(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y
    def translate(self, p):
        """Move to new (x+dx,y+dy)."""
        self.translate_xy(p.x, p.y)
    def translate_xy(self, dx, dy):
        """Move to new (x+dx,y+dy)."""
        self.x = self.x + dx
        self.y = self.y + dy
    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.
        
        Positive y goes *up,* as in traditional mathematics.
        
        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.
        
        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c*self.x - s*self.y, s*self.x + c*self.y)
        return Point(x,y)
    
    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.
        
        Positive y goes *up,* as in traditional mathematics.
        
        The new position is returned as a new Point.
        """
        result = self.clone()
        result.translate(-p.x, -p.y)
        result.rotate(theta)
        result.translate(p.x, p.y)
        return result

class Rect(object):
    """A rectangle identified by two points.

    The rectangle stores left, top, right, and bottom values.

    Coordinates are based on screen coordinates.

  y increases                            top
       ^                                  |
       |                           left  -+-  right
       +-----> x increases                |
    origin                              bottom

    set_points  -- reset rectangle coordinates
    contains  -- is a point inside?
    overlaps  -- does a rectangle overlap?
    top_left  -- get top-left corner
    bottom_right  -- get bottom-right corner
    expanded_by  -- grow (or shrink)
    """
    def __init__(self, pt1, pt2):
        """Initialize a rectangle from two points."""
        self.set_points(pt1, pt2)
    @classmethod
    def from_dimensions(cls, x, y, w, h):
        return Rect(Point(x, y), Point(x + w, y + h))
    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        self.left = min(pt1.x, pt2.x)
        self.top = max(pt1.y, pt2.y)
        self.right = max(pt1.x, pt2.x)
        self.bottom = min(pt1.y, pt2.y)
    def set_points_from_dimensions(self, x, y, w, h):
        """Cheaper and faster set points operation"""
        self.left = x
        self.bottom = y
        self.right = x + w
        self.top = y + h
    def contains(self, o):
        """Return true if a point or rect is completely inside the rectangle."""
        try:
            return (self.left <= o.x <= self.right and
                    self.bottom <= o.y <= self.top)
        except AttributeError:
            r = (self.right >= o.right and self.left <= o.left and
                    self.bottom <= o.bottom and self.top >= o.top)
            return r
    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        return (self.right >= other.left and self.left <= other.right and
                self.top >= other.bottom and self.bottom <= other.top)
    def bottom_left(self):
        """Return the bottom-left corner as a Point."""
        return Point(self.left, self.bottom)
    def top_right(self):
        """Return the top-right corner as a Point."""
        return Point(self.right, self.top)
    def dimension(self):
        """Return x, y, w, h in this order"""
        return self.left, self.bottom, self.right - self.left, self.top - self.bottom
    def expanded_by(self, n):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" points.
        """
        p1 = Point(self.left-n, self.top+n)
        p2 = Point(self.right+n, self.bottom-n)
        return Rect(p1, p2)
    def __str__( self ):
        return "<Rect ({0},{1})-({2},{3})>".format(self.left,self.top,
                                           self.right,self.bottom)
    def __repr__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__,
                               Point(self.left, self.top),
                               Point(self.right, self.bottom))
