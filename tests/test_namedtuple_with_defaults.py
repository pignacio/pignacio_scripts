#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from unittest import TestCase
import logging

from mock import patch, sentinel
from nose.tools import eq_, ok_, raises

from scripts.namedtuple_with_defaults import namedtuple_with_defaults


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@patch('scripts.namedtuple_with_defaults.collections.namedtuple')
def test_nt_with_defs_delegates_to_nt(nt_mock):
    class NTClass(object):  # pylint: disable=too-few-public-methods
        pass
    nt_mock.return_value = NTClass
    tuple_class = namedtuple_with_defaults(sentinel.name, sentinel.fields,
                                           defaults=sentinel.defaults)
    ok_(NTClass in tuple_class.__bases__,
        'NamedTuple is not base of returned tuple class')
    nt_mock.assert_called_once_with(sentinel.name, sentinel.fields)


class NamedtupleWithDefaultsTest(TestCase):
    def setUp(self):
        self.tuple_class = namedtuple_with_defaults(
            'TestTuple', ['a', 'b', 'c'],
            defaults=dict(b=sentinel.b_default))

    def test_full_args(self):
        value = self.tuple_class(sentinel.a, sentinel.b,
                                 sentinel.c)
        eq_(value.a, sentinel.a)
        eq_(value.b, sentinel.b)
        eq_(value.c, sentinel.c)

    def test_full_kwargs(self):
        value = self.tuple_class(a=sentinel.a, b=sentinel.b,
                                 c=sentinel.c)
        eq_(value.a, sentinel.a)
        eq_(value.b, sentinel.b)
        eq_(value.c, sentinel.c)

    def test_default_is_set(self):
        value = self.tuple_class(sentinel.a, c=sentinel.c)
        eq_(value.a, sentinel.a)
        eq_(value.b, sentinel.b_default)
        eq_(value.c, sentinel.c)

    @raises(ValueError)
    def test_missing_arg_fails(self):
        self.tuple_class(sentinel.a, sentinel.c)


class GetDefaultsTest(TestCase):
    def setUp(self):
        class TupleClass(namedtuple_with_defaults('TestTuple', 'a,b,c')):  # pylint: disable=too-few-public-methods
            @classmethod
            def _get_defaults(cls):
                return dict(b=sentinel.b_default)
        self.tuple_class = TupleClass

    def test_default_is_set(self):
        value = self.tuple_class(sentinel.a, c=sentinel.c)
        eq_(value.a, sentinel.a)
        eq_(value.b, sentinel.b_default)
        eq_(value.c, sentinel.c)
