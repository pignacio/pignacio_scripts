#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import collections
import json
import logging
import sys

from astroid import MANAGER, nodes, inference_tip, UseInferenceDefault, BRAIN_MODULES_DIR
from astroid.builder import AstroidBuilder

sys.path.append(BRAIN_MODULES_DIR)
import py2stdlib

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _looks_like_nt_with_defaults(node):
    func = node.func
    if type(func) == nodes.Getattr:
        return func.attrname == 'namedtuple_with_defaults'
    elif type(func) == nodes.Name:
        return func.name == 'namedtuple_with_defaults'
    return False


def nt_with_defaults_transform(node, *args, **kwargs):
    node.args = node.args[:2]
    return py2stdlib.infer_named_tuple(node, *args, **kwargs)


def register(_linter):
    pass


MANAGER.register_transform(nodes.CallFunc, inference_tip(nt_with_defaults_transform),
                           _looks_like_nt_with_defaults)
