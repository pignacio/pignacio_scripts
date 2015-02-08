#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from __future__ import absolute_import, unicode_literals

import logging

from nose.tools import eq_, ok_
from unittest import TestCase

from scripts.sentinels import Sentinels


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def noteq(a, b):
    return ok_(a != b, "{} == {}".format(a, b))


def same(a, b):
    return ok_(a is b, "{} is not {}".format(a, b))


def notsame(a, b):
    return ok_(a is not b, "{} is {}".format(a, b))


class SentinelsTests(TestCase):
    def setUp(self):
        self.sentinels = Sentinels()

    def equal_attrs_return_same_sentinels_test(self):
        first = self.sentinels.name
        second = self.sentinels.name
        same(first, second)

    def diff_attrs_return_not_same_sentinels_test(self):
        first = self.sentinels.name
        second = self.sentinels.other_name
        notsame(first, second)

    def equal_attrs_return_equal_sentinels_test(self):
        first = self.sentinels.name
        second = self.sentinels.name
        eq_(first, second)
        eq_(second, first)

    def diff_attrs_return_diff_sentinels_test(self):
        first, second = self.sentinels.name, self.sentinels.other_name
        noteq(first, second)
        noteq(second, first)

    def attrs_and_keys_return_equal_sentinels_test(self):
        by_attr = self.sentinels.name
        by_key = self.sentinels['name']
        eq_(by_attr, by_key)
        eq_(by_key, by_attr)

    def attrs_and_keys_return_same_sentinels_test(self):
        by_attr = self.sentinels.name
        by_key = self.sentinels['name']
        same(by_attr, by_key)
