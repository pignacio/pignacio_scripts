#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from __future__ import absolute_import, unicode_literals

import collections
import logging

from nose.tools import eq_, raises

from scripts.mock_namedtuple import mock_namedtuple, UnmockedField


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


NamedTuple = collections.namedtuple("NamedTuple", ['a', 'b', 'c'])
MockTuple = mock_namedtuple(NamedTuple)


def fields_are_correctly_inited_test():
    mock_tuple = MockTuple(a=3, c=5)
    eq_(mock_tuple.a, 3)
    eq_(mock_tuple.c, 5)
    eq_(MockTuple(b=7).b, 7)


@raises(UnmockedField)
def cannot_access_unmocked_fields_test():
    MockTuple(a=3).b


@raises(ValueError)
def init_missing_field_fails_test():
    MockTuple(missing=True)


@raises(AttributeError)
def mocked_fields_cannot_be_set_test():
    MockTuple(a=3).a = 5


@raises(UnmockedField, AttributeError)
def unmocked_field_cannot_be_set_test():
    MockTuple().a = 1


def replace_works_on_mocked_fields_test():
    mock_tuple = MockTuple(a=1, b=2)
    new_tuple = mock_tuple._replace(a=3)
    eq_(new_tuple.a, 3)
    eq_(new_tuple.b, 2)


def replace_works_on_unmocked_fields_test():
    new_tuple = MockTuple(a=1)._replace(b=2)
    eq_(new_tuple.b, 2)


@raises(ValueError)
def replace_fails_on_missing_fields_test():
    MockTuple(a=1)._replace(missing=2)
