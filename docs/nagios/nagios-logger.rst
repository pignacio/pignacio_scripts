.. _nagios/nagios-logger:

========================================================
NagiosLogger: A helper for creating nagios/icinga alarms
========================================================

Nagios has some quirks when it comes to running a check script, which makes
creating and debugging good checks complex:

* stderr is not reported. So, if a naive python alarm fails unexpectedly, all
  you get through the web interface is a warn status and "(null)" as the
  script output.

* The first line of output is special, beacuse its shown in the service list
  view. I found providing the correct information in this first line can help
  a lot when it comes to finding whats wrong in a failing system. A simple
  print or log statement anywhere can break this.

* Empty lines are replaced with a literal ``\n``.

:py:class:`~pignacio_scripts.nagios.logger.NagiosLogger` does a variety of
things to solve this problems, and help when writing checks, namely:

* stderr is redirected to classical stdout. If something writes there, you get
  it on the service output.

* stdout is buffered, and rendered at the end of the service output. This
  allows for print statements and logging in the middle of the check without
  worrying about moving the first line.

* Empty lines are replaced with (non-empty) whitespace.

* logging is configured at INFO level by default.

* Unexpected exceptions are logged and the check exits in a graceful manner
  with a UNK status.

* Provides an API to log errors, warnings and important stuff. This is used to
  determine the check status (OK/WARN/CRIT), show the most relevant stuff in
  the first line, and create a report between the first line and the buffered
  stdout

* Remembers the exit code for each status for you ;)

An example showing this features and the basic usage:

.. code:: python

  from pignacio_scripts.nagios import NagiosLogger

  def main():
    print 'Fetching the queue size'
    size = get_queue_size()
    NagiosLogger.important('Queue size: {}'.format(size))
    if size > 1000:
        NagiosLogger.error('Queue size is bigger than 1000')
    if size > 200:
        NagiosLogger.warning('Queue size is bigger than 200')
    return "This will be shown in the first line if there were no errors"


  if __name__ == '__main__':
      NagiosLogger.run(main)
