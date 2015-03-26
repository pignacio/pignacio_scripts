#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,invalid-name
from __future__ import absolute_import, unicode_literals, division

import unittest
import logging


from pignacio_scripts.testing.testcase import TestCase
from pignacio_scripts.testing.mock import patch, sentinel, Mock


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TestCaseTest(unittest.TestCase):
    class MyTestCase(TestCase):
        def runTest(self):
            pass

    def setUp(self):
        self.testcase = self.MyTestCase()
        fail_patcher = patch.object(self.testcase, 'fail', autospec=True)
        self.addCleanup(fail_patcher.stop)
        self.mock_fail = fail_patcher.start()
        cleanup_patcher = patch.object(self.testcase, 'addCleanup',
                                       autospec=True)
        self.addCleanup(cleanup_patcher.stop)
        self.mock_cleanup = cleanup_patcher.start()

    def test_is_unittest_subclass(self):
        self.assertIsInstance(self.testcase, unittest.TestCase)

    @patch('pignacio_scripts.testing.testcase.patch', autospec=True)
    def test_patch(self, mock_patch):
        patcher = Mock()
        patcher.start.return_value = sentinel.patched
        mock_patch.return_value = patcher

        patched = self.testcase.patch(sentinel.arg, kwarg=sentinel.kwvalue)

        self.assertEqual(patched, sentinel.patched)
        mock_patch.assert_called_once_with(sentinel.arg,
                                           kwarg=sentinel.kwvalue)
        patcher.start.assert_called_once_with()
        self.mock_cleanup.assert_any_call(patcher.stop)

    @patch('pignacio_scripts.testing.testcase.patch')
    def test_patch_object(self, mock_patch):
        patcher = Mock()
        patcher.start.return_value = sentinel.patched
        mock_patch.object.return_value = patcher

        patched = self.testcase.patch_object(sentinel.arg,
                                             kwarg=sentinel.kwvalue)

        self.assertEqual(patched, sentinel.patched)
        mock_patch.object.assert_called_once_with(sentinel.arg,
                                                  kwarg=sentinel.kwvalue)
        patcher.start.assert_called_once_with()
        self.mock_cleanup.assert_any_call(patcher.stop)

    @patch('pignacio_scripts.testing.testcase.capture_stdout')
    def test_capture_stdout(self, mock_capture):
        patcher = Mock()
        patcher.start.return_value = sentinel.patched
        mock_capture.return_value = patcher

        patched = self.testcase.capture_stdout()

        self.assertEqual(patched, sentinel.patched)
        mock_capture.assert_called_once_with()
        patcher.start.assert_called_once_with()
        self.mock_cleanup.assert_any_call(patcher.stop)

    def test_assert_size_good(self):
        self.testcase.assertSize([1, 2, 3], 3)
        self.assertFalse(self.mock_fail.called)

    def test_assert_size_bad(self):
        self.testcase.assertSize([1, 2], 3)
        self.assertTrue(self.mock_fail.called)
        self.assertIn('size is 2 != 3', self.mock_fail.call_args[0][0])

    def test_assert_size_fails_with_no_len(self):
        self.testcase.assertSize(1, 1)
        self.assertTrue(self.mock_fail.called)
        self.assertIn('Could not get 1 size', self.mock_fail.call_args[0][0])
