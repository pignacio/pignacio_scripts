#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import collections
import logging
import sys


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def namedtuple_with_defaults(tuple_name, fields, defaults=None):
    defaults = defaults or {}
    tuple_class = collections.namedtuple(tuple_name, fields)
    class NamedTuple(tuple_class):
        __defaults = defaults

        def __new__(cls, *args, **kwargs):
            defaults = cls._get_defaults()
            fields_in_args = set(tuple_class._fields[:len(args)])
            kwvalues = {f: cls.__get_value(f, kwargs, defaults)
                        for f in tuple_class._fields if f not in fields_in_args}
            return tuple_class.__new__(cls, *args, **kwvalues)  # pylint: disable=star-args

        @staticmethod
        def __get_value(key, kwargs, defaults):
            try:
                return kwargs[key]
            except KeyError:
                try:
                    return defaults[key]
                except KeyError:
                    raise ValueError("Missing argument for namedtuple: '{}'"
                                     .format(key))
        @classmethod
        def _get_defaults(cls):
            return cls.__defaults

    NamedTuple.__name__ = str(tuple_name)  # Prevent unicode in Python 2.x

    # Stolen from: collections.namedtuple
    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        NamedTuple.__module__ = sys._getframe(1).f_globals.get('__name__',
                                                               '__main__')
    except (AttributeError, ValueError):
        pass
    # /Stolen
    return NamedTuple
