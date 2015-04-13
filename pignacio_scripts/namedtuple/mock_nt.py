#! /usr/bin/env python
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
from __future__ import absolute_import, unicode_literals

import logging

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def mock_namedtuple_class(tuple_class):
    """
    Create a partially constructible namedtuple class, wrapping
    ``tuple_class``.

    This allow for construction of testing stubs using only
    the needed data fields, and avoids issues if an unrelated part of the
    namedtuple schema changes.

    Args:
        tuple_class(type): Namedtuple class to wrap
    Return:
        The corresponding mock namedtuple class

    >>> Tuple = collections.namedtuple('Tuple', ['a', 'b'])
    >>> MockTuple = mock_namedtuple_class(Tuple)
    >>> MockTuple(a=3).a
    3
    >>> MockTuple(a=3).b
    Traceback (most recent call last):
      [...]
    AttributeError: Missing 'b' field in 'Tuple' mock. (id=140371982628528)

    """

    class MockTuple(tuple_class):
        # pylint: disable=no-init,too-few-public-methods
        __EXCEPTION_SENTINEL = object()

        def __new__(cls, **kwargs):
            for field in kwargs:
                if field not in tuple_class._fields:
                    raise ValueError("'{}' is not a valid field for {}".format(
                        field, tuple_class))
            values = [kwargs.get(f, cls.__EXCEPTION_SENTINEL)
                      for f in tuple_class._fields]
            return tuple_class.__new__(cls, *values)

        def __getattribute__(self, attr):
            # Avoid recursion filtering self._* lookups without doing self._*
            # lookups
            value = tuple_class.__getattribute__(self, attr)
            if attr.startswith("_"):
                return value
            if value == self.__EXCEPTION_SENTINEL:
                raise AttributeError("Missing '{}' field in '{}' mock. (id={})"
                                     .format(attr, tuple_class.__name__,
                                             id(self)))
            return value

    return MockTuple


def mock_namedtuple(tuple_class, **kwargs):
    """
    Create a mock namedtuple instance, with the given ``tuple_class`` and
    ``kwargs``.

    Args:
        tuple_class(type): Namedtuple class to wrap
        **kwargs: fields of the namedtuple to instantiate
    Return:
        The corresponding mock namedtuple instance

    >>> Tuple = collections.namedtuple('Tuple', ['a', 'b'])
    >>> mock_namedtuple(Tuple, b=5).b
    5
    """
    return mock_namedtuple_class(tuple_class)(**kwargs)
