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

from .capture import capture_stdout
from .testcase import TestCase

__all__ = ['capture_stdout', 'TestCase']
