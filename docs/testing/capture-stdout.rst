.. _testing/capture-stdout:

================
Capturing stdout
================


You can capture the standard output stream using the
:py:func:`~pignacio_scripts.testing.capture.capture_stdout` function.

It works as a context manager, using the with statement:

.. code:: python

  >>> with capture_stdout() as captured:
  >>>     print "Hello!"
  >>> captured.getvalue()
  "Hello!\n"


Also, it can be used as a decorator, to wrap a test function. The additional
argument is added at the end (the same as patch decorators).

.. code:: python

  class SomeTests(TestCase):
      @capture_stdout
      def test_with_stdout(self, stdout):
          print "Ohai"
          print "Kthxbye"
          self.assertEqual(stdout.getvalue(), 'Ohai\nKthxbye\n')
