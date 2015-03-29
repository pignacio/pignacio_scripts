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
import sys

from astroid import MANAGER, nodes, inference_tip, BRAIN_MODULES_DIR

sys.path.append(BRAIN_MODULES_DIR)
import py2stdlib

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _looks_like_nt_with_defaults(node):
    func = node.func
    if type(func) == nodes.Getattr:  # pylint: disable=unidiomatic-typecheck
        return func.attrname == 'namedtuple_with_defaults'
    elif type(func) == nodes.Name:  # pylint: disable=unidiomatic-typecheck
        return func.name == 'namedtuple_with_defaults'
    return False


def nt_with_defaults_transform(node, *args, **kwargs):
    node.args = node.args[:2]
    return py2stdlib.infer_named_tuple(node, *args, **kwargs)


def register(_linter):
    pass


MANAGER.register_transform(nodes.CallFunc,
                           inference_tip(nt_with_defaults_transform),
                           _looks_like_nt_with_defaults)
