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

import inspect, functools
def _autoset(init, self, *args, **kwargs):
    spec = inspect.getargspec(init)
    argval = {}
    if spec.defaults is not None:
        for i in range(len(spec.defaults), 0, -1):
            name = spec.args[-i]
            argval[name] = spec.defaults[-i]
    for i in range(len(args)):
        argval[spec.args[i + 1]] = args[i]
    for n in kwargs:
        argval[n] = kwargs[n]
    for n in argval:
        self.__setattr__(n, argval[n])

def autoset(f):
    """Decoration that turns all arguments of an init function
into attributes of the created object."""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        _autoset(f, self, *args, **kwargs)
        f(self, *args, **kwargs)
    return wrapper

class __partial(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def __call__(self, *nargs, **kwargs):
        return partial(self, *nargs, **kwargs)

def _partial(f, *nargs, **nkwargs):
    if not inspect.isfunction(f):
        args, kwargs = f.args, f.kwargs
        spec = inspect.getargspec(f.func)
        f = f.func
    else:
        args, kwargs = [], {}
        spec = inspect.getargspec(f)
    args += nargs
    kwargs.update(nkwargs)
    total = len(spec.args)
    if spec.defaults is not None:
        total -= len(spec.defaults)
    if len(args) + len(kwargs) < total:
        return _partial(f, *args, **kwargs)
    else:
        return f(*args, **kwargs)

def partial(f):
    """Decoration that gives haskell-ish powers to functions"""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        _partial(f, self, *args, **kwargs)
        f(self, *args, **kwargs)
    return wrapper
