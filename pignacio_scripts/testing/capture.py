#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import, unicode_literals, division, print_function)

import logging
import sys
from six import StringIO


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Capturer(object):
    def __init__(self, obj, attribute):
        self._obj = obj
        self._attribute = attribute
        self._original = None
        self._started = False

    def start(self):
        if self._started:
            raise ValueError('Capturer is already started')
        self._original = getattr(self._obj, self._attribute)
        captured = StringIO()
        setattr(self._obj, self._attribute, captured)
        self._started = True
        return captured

    def stop(self):
        if not self._started:
            raise ValueError('Stopping non-started Capturer')
        setattr(self._obj, self._attribute, self._original)
        self._started = False

    def __enter__(self):
        return self.start()

    def __exit__(self, *args, **kwargs):
        self.stop()


def capture_stdout(func=None):
    if func is None:
        return Capturer(sys, 'stdout')
    else:
        def new_func(*args, **kwargs):
            with capture_stdout() as captured:
                new_args = args + (captured,)
                return func(*new_args, **kwargs)
        return new_func
