#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from __future__ import absolute_import, unicode_literals

import sys


__all__ = ['create_autospec', 'patch', 'sentinel', 'Mock', 'MagicMock']


# python version based mock module:
if sys.version_info[0] == 2:
    import mock  # pylint: disable=unused-import
else:
    from unittest import mock  # pylint: disable=no-name-in-module,unused-import


create_autospec = mock.create_autospec
patch = mock.patch
sentinel = mock.sentinel
Mock = mock.Mock
MagicMock = mock.MagicMock
