#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,invalid-name
from __future__ import (
    absolute_import, unicode_literals, division, print_function)

import logging
import sys

from pignacio_scripts.testing import TestCase
from pignacio_scripts.testing.mock import sentinel, patch, Mock
from pignacio_scripts.nagios import NagiosLogger
from pignacio_scripts.nagios.logger import (
    get_first_line_message, get_first_line, print_and_exit, list_messages,
    get_output, print_lines, LoggerStatus, empty_lines_to_whitespace
)


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class InitialStatusTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus.initial()

    def test_exit_status(self):
        self.assertEqual(self.status.unknown, False)

    def test_errors(self):
        self.assertSize(self.status.errors, 0)

    def test_warnings(self):
        self.assertSize(self.status.warnings, 0)

    def test_important(self):
        self.assertSize(self.status.important, 0)


class ExitCodeTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus.initial()

    def test_initial_exit_code(self):
        self.assertEqual(self.status.exit_code(), LoggerStatus.EXIT_OK)

    def test_unknown_exit_code(self):
        status = self.status.set_unknown()
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_unknown_beats_error(self):
        status = self.status.set_unknown()
        status = status.add_error('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_unknown_beats_warning(self):
        status = self.status.set_unknown()
        status = status.add_warning('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_unknown_beats_important(self):
        status = self.status.set_unknown()
        status = status.add_important('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_error_exit_code(self):
        status = self.status.add_error('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_CRIT)

    def test_error_beats_warning(self):
        status = self.status.add_error('message')
        status = status.add_warning('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_CRIT)

    def test_error_beats_important(self):
        status = self.status.add_error('message')
        status = status.add_important('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_CRIT)

    def test_warning_exit_code(self):
        status = self.status.add_warning('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_WARN)

    def test_warning_beats_important(self):
        status = self.status.add_warning('message')
        status = status.add_important('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_WARN)

    def test_important_is_ok(self):
        status = self.status.add_important('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_OK)


class AddStuffTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus(
            unknown=sentinel.unknown,
            errors=sentinel.errors,
            warnings=sentinel.warnings,
            important=sentinel.important,
        )

    def test_add_error(self):
        status = self.status._replace(errors=())
        status = status.add_error("<message_1>")
        status = status.add_error("<message_2>")
        self.assertSize(status.errors, 2)
        self.assertEqual(status.errors[0], "<message_1>")
        self.assertEqual(status.errors[1], "<message_2>")
        self.assertEqual(status.unknown, sentinel.unknown)
        self.assertEqual(status.warnings, sentinel.warnings)
        self.assertEqual(status.important, sentinel.important)

    def test_add_warning(self):
        status = self.status._replace(warnings=())
        status = status.add_warning("<message_1>")
        status = status.add_warning("<message_2>")
        self.assertSize(status.warnings, 2)
        self.assertEqual(status.warnings[0], "<message_1>")
        self.assertEqual(status.warnings[1], "<message_2>")
        self.assertEqual(status.unknown, sentinel.unknown)
        self.assertEqual(status.errors, sentinel.errors)
        self.assertEqual(status.important, sentinel.important)

    def test_add_important(self):
        status = self.status._replace(important=())
        status = status.add_important("<message_1>")
        status = status.add_important("<message_2>")
        self.assertSize(status.important, 2)
        self.assertEqual(status.important[0], "<message_1>")
        self.assertEqual(status.important[1], "<message_2>")
        self.assertEqual(status.unknown, sentinel.unknown)
        self.assertEqual(status.errors, sentinel.errors)
        self.assertEqual(status.warnings, sentinel.warnings)

    def test_set_unknown(self):
        status = self.status._replace(unknown=False)
        status = status.set_unknown()
        self.assertEqual(status.unknown, True)
        self.assertEqual(status.important, sentinel.important)
        self.assertEqual(status.errors, sentinel.errors)
        self.assertEqual(status.warnings, sentinel.warnings)


class GetFirstLineMessageTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus.initial()

    def _test_line(self, status, line, message=None):
        self.assertEqual(get_first_line_message(status, message), line)

    def test_no_errors_no_warnings(self):
        self._test_line(self.status, '')

    def test_one_error_no_warnings(self):
        status = self.status.add_error('<err_msg>')
        self._test_line(status, 'Error: <err_msg>.')

    def test_multiple_error_no_warnings(self):
        status = self.status.add_error('<err_msg>')
        status = status.add_error('<err_msg_2>')
        self._test_line(status, '2 errors (First: <err_msg>).')

    def test_no_errors_one_warning(self):
        status = self.status.add_warning('<wng_msg>')
        self._test_line(status, 'Warning: <wng_msg>.')

    def test_one_error_one_warning(self):
        status = self.status.add_error('<err_msg>')
        status = status.add_warning('<wng_msg>')
        self._test_line(status, ('Error: <err_msg>.'))

    def test_multiple_error_one_warning(self):
        status = self.status.add_error('<err_msg>')
        status = status.add_error('<err_msg_2>')
        status = status.add_warning('<wng_msg>')
        self._test_line(status, '2 errors (First: <err_msg>).')

    def test_no_errors_multiple_warnings(self):
        status = self.status.add_warning('<wng_msg>')
        status = status.add_warning('<wng_msg_2>')
        self._test_line(status, '2 warnings (First: <wng_msg>).')

    def test_one_error_multiple_warnings(self):
        status = self.status.add_error('<err_msg>')
        status = status.add_warning('<wng_msg>')
        status = status.add_warning('<wng_msg_2>')
        self._test_line(status, 'Error: <err_msg>.')

    def test_multiple_error_multiple_warnings(self):
        status = self.status.add_error('<err_msg>')
        status = status.add_error('<err_msg_2>')
        status = status.add_warning('<wng_msg>')
        status = status.add_warning('<wng_msg_2>')
        self._test_line(status, '2 errors (First: <err_msg>).')

    def test_message_is_shown(self):
        self._test_line(self.status, '<message>', message='<message>')

    def test_warning_hides_message(self):
        status = self.status.add_warning('<warning>')
        self._test_line(status, 'Warning: <warning>.', message="<message>")

    def test_error_hides_message(self):
        status = self.status.add_error('<error>')
        self._test_line(status, 'Error: <error>.', message="<message>")

    def test_unknown_state_default_mesage(self):
        status = self.status.set_unknown()
        status = status.add_error('<error>')
        status = status.add_warning('<warning>')
        self._test_line(status, 'Something unexpected happened')

    def test_unknown_state_forces_message(self):
        status = self.status.set_unknown()
        status = status.add_error('<error>')
        status = status.add_warning('<warning>')
        self._test_line(status, '<message>', message="<message>")


class GetFirstLineTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus.initial()
        self.mock_exit_code = self.patch_object(self.status, 'exit_code',
                                                autospec=True)
        self.mock_exit_code.return_value = LoggerStatus.EXIT_OK

    def test_shows_ok_status(self):
        line = get_first_line(self.status)
        self.assertTrue(line.startswith('STATUS: OK.'))

    def test_shows_warn_status(self):
        self.mock_exit_code.return_value = LoggerStatus.EXIT_WARN
        line = get_first_line(self.status)
        self.assertTrue(line.startswith('STATUS: WARNING.'))

    def test_shows_crit_status(self):
        self.mock_exit_code.return_value = LoggerStatus.EXIT_CRIT
        line = get_first_line(self.status)
        self.assertTrue(line.startswith('STATUS: CRITICAL.'))

    def test_shows_unk_status(self):
        self.mock_exit_code.return_value = LoggerStatus.EXIT_UNK
        line = get_first_line(self.status)
        self.assertTrue(line.startswith('STATUS: UNKNOWN.'))

    @patch('pignacio_scripts.nagios.logger.get_first_line_message',
           autospec=True)
    def test_appends_first_line_message(self, mock_get_message):
        mock_get_message.return_value = '<line_message>'
        line = get_first_line(self.status, sentinel.message)

        self.assertIn('<line_message>', line)
        mock_get_message.assert_called_once_with(self.status, sentinel.message)


class PrintAndExitTests(TestCase):
    def setUp(self):
        self.mock_get_output = self.patch(
            'pignacio_scripts.nagios.logger.get_output',
            autospec=True)
        self.mock_get_output.return_value = sentinel.output
        self.mock_print_lines = self.patch(
            'pignacio_scripts.nagios.logger.print_lines', autospec=True)
        self.mock_sys_exit = self.patch(
            'pignacio_scripts.nagios.logger.sys.exit', autospec=True)
        self.mock_empty_to_whitespace = self.patch(
            'pignacio_scripts.nagios.logger.empty_lines_to_whitespace',
            autospec=True)
        self.mock_empty_to_whitespace.return_value = sentinel.whitespace_output
        self.status = LoggerStatus(
            unknown=sentinel.unknown,
            warnings=sentinel.warnings,
            errors=sentinel.errors,
            important=sentinel.important,
        )
        self.mock_exit_code = self.patch_object(self.status, 'exit_code',
                                                autospec=True)
        self.mock_exit_code.return_value = sentinel.exit_code

    def test_exit_is_called(self):
        print_and_exit(self.status, sentinel.additional)
        self.mock_sys_exit.assert_called_once_with(sentinel.exit_code)

    def test_message_is_proxied(self):
        print_and_exit(self.status, sentinel.additional, sentinel.message)
        self.mock_get_output.assert_called_once_with(self.status,
                                                     sentinel.additional,
                                                     sentinel.message)

    def test_get_output_is_called(self):
        print_and_exit(self.status, sentinel.additional)
        self.mock_get_output.assert_called_once_with(self.status,
                                                     sentinel.additional,
                                                     None)

    def test_output_is_printed(self):
        # Must print when sys.exit effectively kills the program
        self.mock_sys_exit.side_effect = iter([SystemExit()])
        try:
            print_and_exit(self.status, sentinel.additional)
        except SystemExit:
            pass
        self.mock_print_lines.assert_called_once_with(
            sentinel.whitespace_output)

    def test_output_is_whitespaced(self):
        print_and_exit(self.status, sentinel.additional)
        self.mock_empty_to_whitespace.assert_called_once_with(sentinel.output)

    def test_system_exit_is_not_swallowed(self):
        self.mock_sys_exit.side_effect = iter([SystemExit()])
        self.assertRaises(SystemExit, print_and_exit, self.status,
                          sentinel.additional)


class ListMessagesTests(TestCase):
    def setUp(self):
        self.messages = [
            '<message_1>',
            '<message_2>',
        ]

    def test_two_messages(self):
        self.assertEqual(list_messages(self.messages, '<LABEL>'), [
            '<LABEL> (2):',
            ' - <message_1>',
            ' - <message_2>',
            '',
        ])

    def test_three_messages(self):
        self.messages.append('<message_3>')
        self.assertEqual(list_messages(self.messages, '<LABEL>'), [
            '<LABEL> (3):',
            ' - <message_1>',
            ' - <message_2>',
            ' - <message_3>',
            '',
        ])

    def test_no_messages(self):
        self.assertEqual(list_messages([], '<LABEL>'), [])


class GetOutputTests(TestCase):
    def setUp(self):
        self.mock_list_messages = self.patch(
            'pignacio_scripts.nagios.logger.list_messages',
            autospec=True)
        self.mock_get_first_line = self.patch(
            'pignacio_scripts.nagios.logger.get_first_line',
            autospec=True)

        list_message_returns = {
            sentinel.errors: [sentinel.listed_errors],
            sentinel.warnings: [sentinel.listed_warnings],
            sentinel.important: [sentinel.listed_important],
        }
        self.mock_list_messages.side_effect = (
            lambda x, *a, **kw: list_message_returns.get(x, []))
        self.mock_get_first_line.return_value = sentinel.first_line

        self.status = LoggerStatus(
            unknown=sentinel.unknown,
            errors=sentinel.errors,
            warnings=sentinel.warnings,
            important=sentinel.important,
        )

    def test_calls_get_first_line(self):
        get_output(self.status, 'additional')
        self.mock_get_first_line.assert_called_once_with(self.status, None)

    def test_proxies_message(self):
        get_output(self.status, 'additional', sentinel.message)
        self.mock_get_first_line.assert_called_once_with(self.status,
                                                         sentinel.message)

    def test_list_messages_calls(self):
        get_output(self.status, 'additional')
        self.mock_list_messages.assert_any_call(sentinel.errors, 'ERRORS')
        self.mock_list_messages.assert_any_call(sentinel.warnings, 'WARNINGS')
        self.mock_list_messages.assert_any_call(
            sentinel.important, 'IMPORTANT')
        self.assertEqual(self.mock_list_messages.call_count, 3)

    def test_output_order(self):
        output = get_output(self.status, 'additional')
        self.assertEqual(output, [
            sentinel.first_line,
            '',
            sentinel.listed_errors,
            sentinel.listed_warnings,
            sentinel.listed_important,
            'Additional info:',
            'additional',
        ])

    def test_additional_is_split(self):
        output = get_output(self.status, '<additional_1>\n<additional_2>')
        self.assertEqual(['<additional_1>', '<additional_2>'], output[-2:])


class PrintLinesTests(TestCase):
    def setUp(self):
        self.stdout = self.capture_stdout()

    def test_empty(self):
        print_lines([])
        self.assertEqual(self.stdout.getvalue(), '')

    def test_list(self):
        print_lines(['<line_1>', '<line_2>', '<line_3>'])
        self.assertEqual(self.stdout.getvalue(),
                         '<line_1>\n<line_2>\n<line_3>\n')

    def test_iter(self):
        print_lines(iter(['<line_1>', '<line_2>', '<line_3>']))
        self.assertEqual(self.stdout.getvalue(),
                         '<line_1>\n<line_2>\n<line_3>\n')


class EmptyLinesToWhitespaceTests(TestCase):
    def test_empties(self):
        lines = empty_lines_to_whitespace(['', ''])
        self.assertSize(lines, 2)
        for line in lines:
            self.assertNotEqual(line, '')
            self.assertEqual(line.strip(), '')
            self.assertNotIn('\n', line)

    def test_non_empties(self):
        original = ['line_1', 'line_2']
        self.assertEqual(empty_lines_to_whitespace(original), original)


class NagiosLoggerResetTests(TestCase):
    def setUp(self):
        self.mock_initial = self.patch_object(LoggerStatus, 'initial')
        self.mock_initial.return_value = sentinel.initial

    def test_status_is_reset(self):
        NagiosLogger.reset()
        self.assertEqual(NagiosLogger.status, sentinel.initial)
        self.mock_initial.assert_called_once_with()


def _guarded_run(func=lambda: None, **kwargs):
    try:
        NagiosLogger.run(func, **kwargs)
    except SystemExit as err:
        return err


class NagiosLoggerRunTests(TestCase):
    def setUp(self):
        self.stdout = self.capture_stdout()
        self.mock_func = Mock(spec=lambda: None)

    def test_raises_system_exit(self):
        self.assertRaises(SystemExit, NagiosLogger.run, lambda: None)

    def test_exits_ok(self):
        err = _guarded_run()
        self.assertEqual(err.code, 0)

    def test_exits_warning(self):
        err = _guarded_run(lambda: NagiosLogger.warning('A warning'))
        self.assertEqual(err.code, 1)

    def test_exits_critical(self):
        err = _guarded_run(lambda: NagiosLogger.error('An error'))
        self.assertEqual(err.code, 2)

    def test_exits_unknown(self):
        err = _guarded_run(lambda: NagiosLogger.unknown_stop('reason'))
        self.assertEqual(err.code, 3)

    @patch('pignacio_scripts.nagios.logger.logging.basicConfig', autospec=True)
    def test_logging_is_configured_on_info(self, mock_config):
        _guarded_run()
        self.assertSoftCalledWith(mock_config, level=logging.INFO)

    @patch('pignacio_scripts.nagios.logger.logging.basicConfig', autospec=True)
    def test_debug_sets_logging_to_debug(self, mock_config):
        _guarded_run(debug=True)
        self.assertSoftCalledWith(mock_config, level=logging.DEBUG)

    def test_func_is_called(self):  # pylint: disable=no-self-use
        _guarded_run(self.mock_func)
        self.mock_func.assert_called_once_with()

    def test_does_not_output_empty_lines(self):
        def run():
            NagiosLogger.important("important\n")
            for x in xrange(10):
                print()
        _guarded_run(run)

        lines = self.stdout.getvalue().splitlines()
        for index, line in enumerate(lines):
            self.assertNotEqual(line, "", "Line #{} was empty".format(index))


class NagiosLoggerRunStdoutTests(TestCase):
    def setUp(self):
        self.stdout = self.capture_stdout()

    def test_contains_stdout(self):
        def func():
            print('<stdout>')

        _guarded_run(func)

        self.assertIn('<stdout>', self.stdout.getvalue())

    @patch('pignacio_scripts.nagios.logger.get_output', autospec=True)
    def test_output_reaches_stdout(self, mock_get_output):
        mock_get_output.return_value = ['<output>']
        _guarded_run()
        self.assertIn('<output>', self.stdout.getvalue())

    @patch('pignacio_scripts.nagios.logger.get_first_line', autospec=True)
    def test_first_line_reaches_stdout(self, mock_get_first_line):
        mock_get_first_line.return_value = '<first_line>'
        _guarded_run()
        self.assertEqual(self.stdout.getvalue().splitlines()[0],
                         '<first_line>')

    def test_unknown_stop_reaches_stdout(self):
        _guarded_run(lambda: NagiosLogger.unknown_stop('<stop_reason>'))
        self.assertIn('<stop_reason>', self.stdout.getvalue())

    def test_run_reads_message_from_function_return(self):
        _guarded_run(lambda: '<message>')
        self.assertIn('<message>', self.stdout.getvalue().splitlines()[0])

    def test_catches_and_logs_errors(self):
        def run():
            raise ValueError("<value>")

        _guarded_run(run)

        first_line = self.stdout.getvalue().splitlines()[0]
        self.assertEqual(
            first_line,
            'STATUS: UNKNOWN. Exception thrown: ValueError, <value>')

    def test_catches_system_exit(self):
        def run():
            sys.exit(255)

        _guarded_run(run)

        first_line = self.stdout.getvalue().splitlines()[0]
        self.assertEqual(first_line,
                         'STATUS: UNKNOWN. Premature exit. Code: 255')


class NagiosLoggerMessagesTests(TestCase):
    def setUp(self):
        NagiosLogger.reset()
        self.mock_status = self.patch_object(NagiosLogger, 'status',
                                             autospec=True)
        self.mock_status.add_error.return_value = sentinel.with_error
        self.mock_status.add_warning.return_value = sentinel.with_warning
        self.mock_status.add_important.return_value = sentinel.with_important

    def test_error(self):
        NagiosLogger.error(sentinel.message)

        self.mock_status.add_error.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_error)

    def test_critical(self):
        NagiosLogger.critical(sentinel.message)

        self.mock_status.add_error.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_error)

    def test_crit(self):
        NagiosLogger.crit(sentinel.message)

        self.mock_status.add_error.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_error)

    def test_warning(self):
        NagiosLogger.warning(sentinel.message)

        self.mock_status.add_warning.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_warning)

    def test_warn(self):
        NagiosLogger.warn(sentinel.message)

        self.mock_status.add_warning.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_warning)

    def test_important(self):
        NagiosLogger.important(sentinel.message)

        self.mock_status.add_important.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_important)

    def test_info(self):
        NagiosLogger.info(sentinel.message)

        self.mock_status.add_important.assert_called_once_with(
            sentinel.message)
        self.assertEqual(NagiosLogger.status, sentinel.with_important)
