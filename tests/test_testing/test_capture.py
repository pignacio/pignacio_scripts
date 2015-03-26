#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,invalid-name
from __future__ import absolute_import, unicode_literals, division

import logging
import six
import sys

from pignacio_scripts.testing import capture_stdout, TestCase
from pignacio_scripts.testing.mock import sentinel

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class CaptureStdoutTests(TestCase):
    def setUp(self):
        self.stdout = six.StringIO()
        self.original = sys.stdout
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout = self.original

    def test_with_statement(self):
        sys.stdout.write('<text_1>')
        with capture_stdout() as captured:
            sys.stdout.write('<text_2>')
        sys.stdout.write('<text_3>')

        self.assertEqual(self.stdout.getvalue(), '<text_1><text_3>')
        self.assertEqual(captured.getvalue(), '<text_2>')

    def test_start_stop(self):
        sys.stdout.write('<text_1>')
        patcher = capture_stdout()
        captured = patcher.start()
        try:
            sys.stdout.write('<text_2>')
        finally:
            patcher.stop()
        sys.stdout.write('<text_3>')

        self.assertEqual(self.stdout.getvalue(), '<text_1><text_3>')
        self.assertEqual(captured.getvalue(), '<text_2>')

    def test_decorator(self):
        @capture_stdout
        def func(captured):
            sys.stdout.write('<text>')
            return captured

        sys.stdout.write('<text_1>')
        captured_stdout = func()  # pylint: disable=no-value-for-parameter
        sys.stdout.write('<text_2>')

        self.assertEqual(captured_stdout.getvalue(), '<text>')
        self.assertEqual(self.stdout.getvalue(), '<text_1><text_2>')

    def test_decorator_add_extra_arg_at_the_end(self):
        @capture_stdout
        def func(*args):
            sys.stdout.write('<text>')
            return args

        # pylint: disable=unbalanced-tuple-unpacking
        argument, captured_stdout = func(sentinel.argument)

        self.assertEqual(argument, sentinel.argument)
        self.assertEqual(captured_stdout.getvalue(), '<text>')

    def test_cannot_start_twice(self):
        original = sys.stdout
        patcher = capture_stdout()
        patcher.start()
        try:
            self.assertRaisesRegexp(ValueError, 'Capturer is already started',
                                    patcher.start)
        finally:
            patcher.stop()
        self.assertEqual(sys.stdout, original)

    def test_cannot_stop(self):
        original = sys.stdout
        patcher = capture_stdout()
        self.assertRaisesRegexp(ValueError, 'Stopping non-started Capturer',
                                patcher.stop)
        self.assertEqual(sys.stdout, original)

    def test_creating_patcher_does_not_patch(self):
        original = sys.stdout
        capture_stdout()
        self.assertEqual(sys.stdout, original)
