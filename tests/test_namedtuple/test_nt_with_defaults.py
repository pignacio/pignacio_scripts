#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,invalid-name
from __future__ import absolute_import, unicode_literals

import logging

from mock import patch, sentinel
from nose.tools import eq_, ok_

from pignacio_scripts.namedtuple import namedtuple_with_defaults
from pignacio_scripts.testing import TestCase

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@patch('pignacio_scripts.namedtuple.nt_with_defaults.collections.namedtuple')
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

    def test_missing_arg_fails(self):
        self.assertRaisesRegexp(ValueError, 'Missing argument for namedtuple',
                                self.tuple_class, sentinel.a, sentinel.b)

    def test_extra_kwargs_fails(self):
        self.assertRaisesRegexp(
            ValueError, 'Unexpected argument for namedtuple',
            self.tuple_class,
            a=sentinel.a, b=sentinel.b, c=sentinel.c, d=sentinel.d)

    def test_extra_args_fails(self):
        self.assertRaisesRegexp(
            ValueError, 'Too many arguments for namedtuple',
            self.tuple_class,
            sentinel.a, sentinel.b, sentinel.c, sentinel.d)


class LambdaDefaultsTest(TestCase):
    def setUp(self):
        # pylint: disable=too-few-public-methods
        self.tuple_class = namedtuple_with_defaults(
            'TestTuple', 'a,b,c', defaults=lambda: {
                'b': sentinel.b_default,
            })

    def test_default_is_set(self):
        value = self.tuple_class(sentinel.a, c=sentinel.c)
        eq_(value.a, sentinel.a)
        eq_(value.b, sentinel.b_default)
        eq_(value.c, sentinel.c)

    def test_mutable_defaults_work(self):
        TestTuple = namedtuple_with_defaults(
            'TestTuple', 'a', defaults=lambda: {
                'a': [],
            })

        first = TestTuple()
        first.a.append('first')
        second = TestTuple()
        second.a.append('second')
        self.assertEqual(first.a, ['first'])
        self.assertEqual(second.a, ['second'])
