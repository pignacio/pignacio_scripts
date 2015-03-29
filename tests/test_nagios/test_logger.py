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
    get_default_first_line, get_first_line, print_and_exit, list_messages,
    get_output, print_lines, LoggerStatus, Message
)


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class InitialStatusTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus.initial()

    def test_exit_status(self):
        self.assertEqual(self.status.unknown, False)

    def test_errors(self):
        self.assertEqual(self.status.errors, [])

    def test_warnings(self):
        self.assertEqual(self.status.warnings, [])

    def test_important(self):
        self.assertEqual(self.status.important, [])


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
        status = status.add_error('message', 'label')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_unknown_beats_warning(self):
        status = self.status.set_unknown()
        status = status.add_warning('message', 'label')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_unknown_beats_important(self):
        status = self.status.set_unknown()
        status = status.add_important('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_UNK)

    def test_error_exit_code(self):
        status = self.status.add_error('message', 'label')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_CRIT)

    def test_error_beats_warning(self):
        status = self.status.add_error('message', 'label')
        status = status.add_warning('message', 'label')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_CRIT)

    def test_error_beats_important(self):
        status = self.status.add_error('message', 'label')
        status = status.add_important('message')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_CRIT)

    def test_warning_exit_code(self):
        status = self.status.add_warning('message', 'label')
        self.assertEqual(status.exit_code(), LoggerStatus.EXIT_WARN)

    def test_warning_beats_important(self):
        status = self.status.add_warning('message', 'label')
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
        status = self.status._replace(errors=[])
        status = status.add_error(sentinel.message_1, sentinel.label_1)
        status = status.add_error(sentinel.message_2, sentinel.label_2)
        self.assertSize(status.errors, 2)
        self.assertEqual(status.errors[0].message, sentinel.message_1)
        self.assertEqual(status.errors[0].label, sentinel.label_1)
        self.assertEqual(status.errors[1].message, sentinel.message_2)
        self.assertEqual(status.errors[1].label, sentinel.label_2)
        self.assertEqual(status.unknown, sentinel.unknown)
        self.assertEqual(status.warnings, sentinel.warnings)
        self.assertEqual(status.important, sentinel.important)

    def test_add_warning(self):
        status = self.status._replace(warnings=[])
        status = status.add_warning(sentinel.message_1, sentinel.label_1)
        status = status.add_warning(sentinel.message_2, sentinel.label_2)
        self.assertSize(status.warnings, 2)
        self.assertEqual(status.warnings[0].message, sentinel.message_1)
        self.assertEqual(status.warnings[0].label, sentinel.label_1)
        self.assertEqual(status.warnings[1].message, sentinel.message_2)
        self.assertEqual(status.warnings[1].label, sentinel.label_2)
        self.assertEqual(status.unknown, sentinel.unknown)
        self.assertEqual(status.errors, sentinel.errors)
        self.assertEqual(status.important, sentinel.important)

    def test_add_important(self):
        status = self.status._replace(important=[])
        status = status.add_important(sentinel.message_1)
        status = status.add_important(sentinel.message_2)
        self.assertSize(status.important, 2)
        self.assertEqual(status.important[0].message, sentinel.message_1)
        self.assertEqual(status.important[1].message, sentinel.message_2)
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


class GetDefaultFirstLineTests(TestCase):
    def setUp(self):
        self.status = LoggerStatus.initial()

    def _test_line(self, status, line):
        self.assertEqual(get_default_first_line(status), line)

    def test_no_errors_no_warnings(self):
        self._test_line(self.status, '')

    def test_one_error_no_warnings(self):
        status = self.status.add_error('<err_msg>', '<err_label>')
        self._test_line(status, 'Error in <err_label>: <err_msg>.')

    def test_multiple_error_no_warnings(self):
        status = self.status.add_error('<err_msg>', '<err_label>')
        status = status.add_error('<err_msg_2>', '<err_label_2>')
        self._test_line(status, 'Errors in (<err_label>,<err_label_2>).')

    def test_no_errors_one_warning(self):
        status = self.status.add_warning('<wng_msg>', '<wng_label>')
        self._test_line(status, 'Warning in <wng_label>: <wng_msg>.')

    def test_one_error_one_warning(self):
        status = self.status.add_error('<err_msg>', '<err_label>')
        status = status.add_warning('<wng_msg>', '<wng_label>')
        self._test_line(status, ('Error in <err_label>: <err_msg>. '
                                 'Warning in <wng_label>: <wng_msg>.'))

    def test_multiple_error_one_warning(self):
        status = self.status.add_error('<err_msg>', '<err_label>')
        status = status.add_error('<err_msg_2>', '<err_label_2>')
        status = status.add_warning('<wng_msg>', '<wng_label>')
        self._test_line(status, ('Errors in (<err_label>,<err_label_2>). '
                                 'Warning in <wng_label>: <wng_msg>.'))

    def test_no_errors_multiple_warnings(self):
        status = self.status.add_warning('<wng_msg>', '<wng_label>')
        status = status.add_warning('<wng_msg_2>', '<wng_label_2>')
        self._test_line(status, 'Warnings in (<wng_label>,<wng_label_2>).')

    def test_one_error_multiple_warnings(self):
        status = self.status.add_error('<err_msg>', '<err_label>')
        status = status.add_warning('<wng_msg>', '<wng_label>')
        status = status.add_warning('<wng_msg_2>', '<wng_label_2>')
        self._test_line(status, ('Error in <err_label>: <err_msg>. '
                                 'Warnings in (<wng_label>,<wng_label_2>).'))

    def test_multiple_error_multiple_warnings(self):
        status = self.status.add_error('<err_msg>', '<err_label>')
        status = status.add_error('<err_msg_2>', '<err_label_2>')
        status = status.add_warning('<wng_msg>', '<wng_label>')
        status = status.add_warning('<wng_msg_2>', '<wng_label_2>')
        self._test_line(status, ('Errors in (<err_label>,<err_label_2>). '
                                 'Warnings in (<wng_label>,<wng_label_2>).'))


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

    def test_appends_message_if_present(self):
        line = get_first_line(self.status, '<message>')
        self.assertEqual(line, 'STATUS: OK. <message>')

    @patch('pignacio_scripts.nagios.logger.get_default_first_line')
    def test_uses_default_line_if_message_is_missing(self, mock_default):
        mock_default.return_value = '<default_line>'
        line = get_first_line(self.status)
        self.assertEqual(line, 'STATUS: OK. <default_line>')
        mock_default.assert_called_once_with(self.status)


class PrintAndExitTests(TestCase):
    def setUp(self):
        self.mock_get_output = self.patch(
            'pignacio_scripts.nagios.logger.get_output', autospec=True)
        self.mock_get_output.return_value = sentinel.output
        self.mock_print_lines = self.patch(
            'pignacio_scripts.nagios.logger.print_lines', autospec=True)
        self.mock_sys_exit = self.patch(
            'pignacio_scripts.nagios.logger.sys.exit', autospec=True)
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
        self.mock_print_lines.assert_called_once_with(sentinel.output)

    def test_system_exit_is_not_swallowed(self):
        self.mock_sys_exit.side_effect = iter([SystemExit()])
        self.assertRaises(SystemExit, print_and_exit, self.status,
                          sentinel.additional)


class ListMessagesTests(TestCase):
    def setUp(self):
        self.messages = [
            Message('<message_1>', '<label_1>'),
            Message('<message_2>', '<label_2>'),
        ]

    def test_with_labels(self):
        self.assertEqual(list_messages(self.messages, '<LABEL>'), [
            '<LABEL> (2):',
            ' - <label_1>: <message_1>',
            ' - <label_2>: <message_2>',
            '',
        ])

    def test_with_no_labels(self):
        self.assertEqual(list_messages(
            self.messages, '<LABEL>',
            include_labels=False), [
                '<LABEL> (2):',
                ' - <message_1>',
                ' - <message_2>',
                '',
            ])

    def test_with_extra_message(self):
        self.messages.append(Message('<message_3>', '<label_3>'))
        self.assertEqual(list_messages(self.messages, '<LABEL>'), [
            '<LABEL> (3):',
            ' - <label_1>: <message_1>',
            ' - <label_2>: <message_2>',
            ' - <label_3>: <message_3>',
            '',
        ])

    def test_empty_messages(self):
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
        get_output(self.status, sentinel.additional)
        self.mock_get_first_line.assert_called_once_with(self.status, None)

    def test_proxies_message(self):
        get_output(self.status, sentinel.additional, sentinel.message)
        self.mock_get_first_line.assert_called_once_with(self.status,
                                                         sentinel.message)

    def test_list_messages_calls(self):
        get_output(self.status, sentinel.additional)
        self.mock_list_messages.assert_any_call(sentinel.errors, 'ERRORS')
        self.mock_list_messages.assert_any_call(sentinel.warnings, 'WARNINGS')
        self.mock_list_messages.assert_any_call(
            sentinel.important, 'IMPORTANT', include_labels=False)
        self.assertEqual(self.mock_list_messages.call_count, 3)

    def test_output_order(self):
        output = get_output(self.status, sentinel.additional)
        self.assertEqual(output, [
            sentinel.first_line,
            '',
            sentinel.listed_errors,
            sentinel.listed_warnings,
            sentinel.listed_important,
            'Additional info:',
            sentinel.additional,
        ])


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


class NagiosLoggerResetTests(TestCase):
    def setUp(self):
        self.mock_initial = self.patch_object(LoggerStatus, 'initial')
        self.mock_initial.return_value = sentinel.initial

    def test_status_is_reset(self):
        NagiosLogger.reset()
        self.assertEqual(NagiosLogger.status, sentinel.initial)
        self.mock_initial.assert_called_once_with()


class NagiosLoggerRunTests(TestCase):
    def setUp(self):
        self.stdout = self.capture_stdout()
        self.mock_print_and_exit = self.patch(
            'pignacio_scripts.nagios.logger.print_and_exit',
            autospec=True,
        )
        self.mock_func = Mock(spec=lambda: None)

    def test_stdout_is_captured_in_additional(self):
        def func():
            print("<inside>")

        print('<before>')
        NagiosLogger.run(func)

        self.assertEqual(self.stdout.getvalue(), '<before>\n')
        self.assertTrue(self.mock_print_and_exit.called)
        additional = self.mock_print_and_exit.call_args[0][1]
        self.assertEqual(additional, '<inside>\n')

    @patch.object(NagiosLogger, 'init')
    def test_init_is_called(self, mock_init):  # pylint: disable=no-self-use
        NagiosLogger.run(lambda: None)
        mock_init.assert_called_once_with(debug=False)

    @patch.object(NagiosLogger, 'init')
    def test_debug_is_proxied(self, mock_init):  # pylint: disable=no-self-use
        NagiosLogger.run(lambda: None, debug=sentinel.debug)
        mock_init.assert_called_once_with(debug=sentinel.debug)

    def test_func_is_called(self):  # pylint: disable=no-self-use
        NagiosLogger.run(self.mock_func)

        self.mock_func.assert_called_once_with()

    @patch.object(NagiosLogger, 'unknown_stop')
    def test_stops_on_system_exit(self, mock_stop):
        self.mock_func.side_effect = iter([SystemExit()])

        NagiosLogger.run(self.mock_func)

        mock_stop.assert_called_once_with("Premature exit")

    @patch('pignacio_scripts.nagios.logger.traceback.print_exception')
    @patch('pignacio_scripts.nagios.logger.sys.exc_info')
    @patch.object(NagiosLogger, 'unknown_stop')
    def test_stops_on_error(self, mock_stop, mock_exc_info, mock_print_exc):
        self.mock_func.side_effect = iter([ValueError("MyError")])
        mock_exc_info.return_value = (IndexError, '<emsg>', sentinel.traceback)

        NagiosLogger.run(self.mock_func)

        mock_stop.assert_called_once_with(
            'Exception thrown: IndexError, <emsg>')
        mock_exc_info.assert_called_once_with()
        mock_print_exc.assert_called_once_with(
            IndexError, '<emsg>', sentinel.traceback, file=sys.stdout)


class NagiosLoggerMessagesTests(TestCase):
    def setUp(self):
        self.mock_status = self.patch_object(NagiosLogger, 'status',
                                             autospec=True)
        self.mock_status.add_error.return_value = sentinel.with_error
        self.mock_status.add_warning.return_value = sentinel.with_warning
        self.mock_status.add_important.return_value = sentinel.with_important

    def test_error(self):
        NagiosLogger.error(sentinel.message, sentinel.label)

        self.mock_status.add_error.assert_called_once_with(
            sentinel.message, sentinel.label)
        self.assertEqual(NagiosLogger.status, sentinel.with_error)

    def test_critical(self):
        NagiosLogger.critical(sentinel.message, sentinel.label)

        self.mock_status.add_error.assert_called_once_with(
            sentinel.message, sentinel.label)
        self.assertEqual(NagiosLogger.status, sentinel.with_error)

    def test_crit(self):
        NagiosLogger.crit(sentinel.message, sentinel.label)

        self.mock_status.add_error.assert_called_once_with(
            sentinel.message, sentinel.label)
        self.assertEqual(NagiosLogger.status, sentinel.with_error)

    def test_warning(self):
        NagiosLogger.warning(sentinel.message, sentinel.label)

        self.mock_status.add_warning.assert_called_once_with(
            sentinel.message, sentinel.label)
        self.assertEqual(NagiosLogger.status, sentinel.with_warning)

    def test_warn(self):
        NagiosLogger.warn(sentinel.message, sentinel.label)

        self.mock_status.add_warning.assert_called_once_with(
            sentinel.message, sentinel.label)
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


class NagiosLoggerUnknownTests(TestCase):
    def setUp(self):
        self.mock_status = self.patch_object(NagiosLogger, 'status',
                                             autospec=True)
        self.mock_print_and_exit = self.patch(
            'pignacio_scripts.nagios.logger.print_and_exit',
            autospec=True)

        self.mock_status.set_unknown.return_value = sentinel.with_unknown

    def test_print_and_exit_is_called(self):
        NagiosLogger.unknown_stop('<stop_message>')

        self.mock_status.set_unknown.assert_called_once_with()
        self.mock_print_and_exit.assert_called_once_with(
            sentinel.with_unknown, '', '<stop_message>')
