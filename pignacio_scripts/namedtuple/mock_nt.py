#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def mock_namedtuple_class(tuple_class):
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
    return mock_namedtuple_class(tuple_class)(**kwargs)
