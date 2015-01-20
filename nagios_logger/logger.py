from __future__ import unicode_literals

import StringIO
import logging
import sys
import traceback


class NagiosLogger(object): # pylint: disable=no-init
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

    # Nagios exit statuses
    _EXIT_OK = 0
    _EXIT_WARN = 1
    _EXIT_CRIT = 2
    _EXIT_UNK = 3

    # Nagios statuses labels
    _STATUS_LABELS = {
        _EXIT_OK: 'OK',
        _EXIT_WARN: 'WARN',
        _EXIT_CRIT: 'CRIT',
        _EXIT_UNK: 'UNK',
    }

    # Pipe replacement for nagios output
    _PIPE_REPL = "__pipe__"

    _buffer = StringIO.StringIO()
    _status = _EXIT_OK
    _errors = []
    _warnings = []
    _importants = []

    @classmethod
    def init(cls, debug=False):
        sys.stdout = cls._buffer
        sys.stderr = sys.__stdout__
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=level)

    @classmethod
    def error(cls, line, label):
        cls._errors.append((line.strip(), label))
        cls._set_status(cls._EXIT_CRIT)

    @classmethod
    def warning(cls, line, label):
        cls._warnings.append((line.strip(), label))
        cls._set_status(cls._EXIT_WARN)

    @classmethod
    def important(cls, line):
        cls._importants.append(line.strip())

    # aliases
    warn = warning
    crit = critical = error
    info = important

    @classmethod
    def unknown_stop(cls, message):
        print message
        cls._set_status(cls._EXIT_UNK)
        cls.print_and_exit(message)

    @classmethod
    def print_and_exit(cls, message=None):
        cls._print_output(message)
        cls._exit()

    @classmethod
    def _print_output(cls, message=None):
        sys.stdout = sys.__stdout__
        print cls._get_first_line(message)
        print
        if cls._errors:
            print "ERRORS (%s)" % len(cls._errors)
            for error, label in cls._errors:
                print " - %s: %s" % (label, error)
            print
        if cls._warnings:
            print "WARNINGS (%s)" % len(cls._warnings)
            for warning, label in cls._warnings:
                print " - %s: %s" % (label, warning)
            print
        if cls._importants:
            print "IMPORTANTS (%s)" % len(cls._importants)
            for important in cls._importants:
                print " - %s" % (important)
            print
        print "Additional info:"
        print cls._buffer.getvalue()

    @classmethod
    def _get_first_line(cls, message=None):
        return "STATUS: %s. %s" % (cls._STATUS_LABELS[cls._status],
                                   message or cls._default_first_line())

    @staticmethod
    def _join_labels(messages):
        return ",".join(msg[1] for msg in messages)

    @classmethod
    def _default_first_line(cls):
        res = StringIO.StringIO()
        if cls._errors:
            if len(cls._errors) > 1:
                print >> res, "Errors in (%s)." % cls._join_labels(cls._errors),
            else:
                print >> res, "Error in %s: %s." % cls._errors[0],
        if cls._warnings:
            if len(cls._warnings) > 1:
                print >> res, ("Warnings in (%s)."
                               % cls._join_labels(cls._warnings)),
            else:
                print >> res, "Warning in %s: %s." % cls._warnings[0],
        return res.getvalue()

    @classmethod
    def _exit(cls):
        sys.exit(cls._status)

    @classmethod
    def run(cls, func, debug=False):
        cls.init(debug=debug)
        try:
            func()
        except Exception:  # pylint: disable=broad-except
            etype, value, trace = sys.exc_info()
            traceback.print_exception(etype, value, trace, file=sys.stdout)
            cls.unknown_stop("Exception thrown : %s, %s" % (etype, value))
        except SystemExit:
            cls.unknown_stop("Premature exit")
        cls.print_and_exit()

    @classmethod
    def _set_status(cls, status):
        cls._status = max(cls._status, status)
