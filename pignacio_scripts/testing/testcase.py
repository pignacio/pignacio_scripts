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
from __future__ import absolute_import, unicode_literals, division

import logging
import unittest
from unittest.util import safe_repr

from .mock import patch
from .capture import capture_stdout


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TestCase(unittest.TestCase):
    def patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patch_object(self, *args, **kwargs):
        patcher = patch.object(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def capture_stdout(self):
        patcher = capture_stdout()
        self.addCleanup(patcher.stop)
        return patcher.start()

    def assertSize(self, obj, size, msg=None):  # pylint: disable=invalid-name
        """Same as self.assertEqual(len(obj), size), with a nicer default
        message."""
        try:
            obj_size = len(obj)
        except Exception:  # pylint: disable=broad-except
            logging.exception("Couldn't get object size")
            self.fail('Could not get {} size.'.format(safe_repr(obj)))
            return

        if size != obj_size:
            standard_msg = "{}'s size is {} != {}".format(
                safe_repr(obj), obj_size, size)
            self.fail(self._formatMessage(msg, standard_msg))
