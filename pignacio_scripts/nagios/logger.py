#!/usr/bin/env python
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
'''
NagiosLogger: A helper for creating nagios/icinga checkers
'''
from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import collections
import logging
import six
import sys
import traceback

_LoggerStatus = collections.namedtuple('LoggerStatus',
                                       ['unknown', 'errors', 'warnings',
                                        'important'])


class UnknownStop(Exception):
    pass


class LoggerStatus(_LoggerStatus):
    # Nagios exit statuses
    EXIT_OK = 0
    EXIT_WARN = 1
    EXIT_CRIT = 2
    EXIT_UNK = 3

    @classmethod
    def initial(cls):
        return cls(unknown=False, errors=(), warnings=(), important=(), )

    def set_unknown(self):
        return self._replace(unknown=True, )

    @staticmethod
    def _append_message(message_list, message):
        return message_list + (message.strip(),)

    def add_error(self, message):
        return self._replace(errors=self._append_message(self.errors, message))

    def add_warning(self, message):
        return self._replace(
            warnings=self._append_message(self.warnings, message))

    def add_important(self, message):
        return self._replace(
            important=self._append_message(self.important, message))

    def exit_code(self):
        if self.unknown:
            return self.EXIT_UNK
        elif self.errors:
            return self.EXIT_CRIT
        elif self.warnings:
            return self.EXIT_WARN
        return self.EXIT_OK


class NagiosLogger(object):  # pylint: disable=no-init
    """ Class for running alarms in nagios/icinga

    Keeps track of errors, warnings and important information, and exits with
    the corresponding exit code for nagios.

    Automatically buffers stdout and stderr and logs errors and warnings
    in an orderly fashion, in order to present the most relevant information
    in the first line of output.

    Basic usage:

    >>> from .logger import NagiosLogger
    >>>
    >>> def main():
    >>>     NagiosLogger.error("This is an error", "ErrorLabel")
    >>>     NagiosLogger.warning("This is an warning", "WarningLabel")
    >>>     NagiosLogger.important("This is something important")
    >>>     if something_is_terribly_wrong:
    >>>         NagiosLogger.unknown_stop("This failed: ... ")
    >>>     NagiosLogger.error("This is an error", "ErrorLabel")
    >>>
    >>> if __name__ == "__main__":
    >>>     NagiosLogger.run(main)
    """

    status = None
    _buffer = six.StringIO()
    original_stdout = None

    # Pipe replacement for nagios output
    _PIPE_REPL = "__pipe__"

    @classmethod
    def init(cls, debug=False):
        cls.reset()
        cls.original_stdout = sys.stdout
        sys.stderr = sys.stdout
        sys.stdout = cls._buffer
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=level, stream=sys.stdout)

    @classmethod
    def reset(cls):
        cls.status = LoggerStatus.initial()
        cls._buffer.seek(0)
        cls._buffer.truncate(0)
        cls.original_stdout = None

    @classmethod
    def _restore_stdout(cls):
        if cls.original_stdout:
            sys.stdout = cls.original_stdout
        cls.original_stdout = None

    @classmethod
    def error(cls, line):
        cls.status = cls.status.add_error(line)

    @classmethod
    def warning(cls, line):
        cls.status = cls.status.add_warning(line)

    @classmethod
    def important(cls, line):
        cls.status = cls.status.add_important(line)

    # aliases
    warn = warning
    crit = critical = error
    info = important

    @classmethod
    def unknown_stop(cls, message):
        cls.status = cls.status.set_unknown()
        raise UnknownStop(message)

    @classmethod
    def run(cls, func, debug=False):
        cls.init(debug=debug)
        try:
            message = func()
        except UnknownStop as stop:
            message = str(stop)
        except Exception:  # pylint: disable=broad-except
            etype, value, trace = sys.exc_info()
            traceback.print_exception(etype, value, trace, file=sys.stdout)
            message = "Exception thrown: %s, %s" % (etype.__name__, value)
            cls.status = cls.status.set_unknown()
        except SystemExit as err:
            etype, value, trace = sys.exc_info()
            traceback.print_exception(etype, value, trace, file=sys.stdout)
            message = "Premature exit. Code: {}".format(err.code)
            cls.status = cls.status.set_unknown()
        cls._restore_stdout()
        print_and_exit(cls.status, cls._buffer.getvalue(), message)


def print_lines(lines):
    for line in lines:
        print(line)


def print_and_exit(status, additional, message=None):
    lines = get_output(status, additional, message)
    print_lines(empty_lines_to_whitespace(lines))
    sys.exit(status.exit_code())


def list_messages(messages, label):
    if not messages:
        return []
    lines = []
    lines.append('{} ({}):'.format(label, len(messages)))
    for message in messages:
        lines.append(' - {}'.format(message))
    lines.append('')
    return lines


def get_output(status, additional, message=None):
    lines = []
    lines.append(get_first_line(status, message))
    lines.append('')
    lines.extend(list_messages(status.errors, 'ERRORS'))
    lines.extend(list_messages(status.warnings, 'WARNINGS'))
    lines.extend(list_messages(status.important, 'IMPORTANT'))
    lines.append('Additional info:')
    lines.extend(additional.splitlines())
    return lines


def empty_lines_to_whitespace(lines):
    return [line if line != '' else ' ' for line in lines]


# Nagios statuses labels
STATUS_LABELS = {
    LoggerStatus.EXIT_OK: 'OK',
    LoggerStatus.EXIT_WARN: 'WARNING',
    LoggerStatus.EXIT_CRIT: 'CRITICAL',
    LoggerStatus.EXIT_UNK: 'UNKNOWN',
}


def get_first_line(status, message=None):
    return "STATUS: %s. %s" % (STATUS_LABELS[status.exit_code()],
                               get_first_line_message(status, message))


def join_labels(messages):
    return ",".join(msg[1] for msg in messages)


def get_first_line_part(messages, label):
    if not messages:
        return ''
    if len(messages) == 1:
        return '{} in {}: {}.'.format(label, messages[0].label,
                                      messages[0].message)
    return '{}s in ({}).'.format(label, join_labels(messages))


def _format_first_line(label, messages):
    if len(messages) == 1:
        return "{}: {}.".format(label.capitalize(), messages[0])
    return "{} {}s (First: {}).".format(len(messages), label, messages[0])


def get_first_line_message(status, message=None):
    if status.unknown:
        return message or 'Something unexpected happened'
    if status.errors:
        return _format_first_line('error', status.errors)
    elif status.warnings:
        return _format_first_line('warning', status.warnings)
    return message or ''
