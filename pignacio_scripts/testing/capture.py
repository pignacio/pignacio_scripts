#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Ignacio Rossi
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import logging
import sys
from six import StringIO

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Capturer(object):
    """ Context manager for patching a stream with a ``StringIO`` instance."""

    def __init__(self, obj, attribute):
        self._obj = obj
        self._attribute = attribute
        self._original = None
        self._started = False

    def start(self):
        """ Replace the target attribute with a ``StringIO`` instance.

        Returns:
            StringIO: The patched stream new value
        """
        if self._started:
            raise ValueError('Capturer is already started')
        self._original = getattr(self._obj, self._attribute)
        captured = StringIO()
        setattr(self._obj, self._attribute, captured)
        self._started = True
        return captured

    def stop(self):
        """ Return the patched attribute to its original state. """
        if not self._started:
            raise ValueError('Stopping non-started Capturer')
        setattr(self._obj, self._attribute, self._original)
        self._started = False

    def __enter__(self):
        return self.start()

    def __exit__(self, *args, **kwargs):
        self.stop()


def capture_stdout(func=None):
    """ Replaces the standard output stream with a ``StringIO`` instance.

    If the argument is supplied, it works as a decorator, adding the captured
    stdout argument at the end of the argument list.

    If not, it works as a context manager.
    """
    if func is None:
        return Capturer(sys, 'stdout')
    else:

        def new_func(*args, **kwargs):
            with capture_stdout() as captured:
                new_args = args + (captured, )
                return func(*new_args, **kwargs)

        return new_func
