.. _testing/testcase:

=====================
Custom TestCase class
=====================

In order to create **and** configure mocks inside ``TestCase.setUp``, there is a
``TestCase`` extension with some methods that proxy ``mock.patch`` and
``mock.patch.object``.

.. code:: python

  from pignacio_scripts.testing import TestCase

  class SomeTests(TestCase):
      def setUp(self):
          self.mock = self.patch('path.to.thing')
          self.mock.return_value = None
          self.mock_object = self.patch_object(thing, 'attribute')

      def test_this(self):
          do_something()
          self.mock.assert_called_once_with()

If you need capturing stdout for all tests in a `TestCase`, you can:

.. code:: python

  class StdoutTests(TestCase):
      def setUp(self):
          self.stdout = self.capture_stdout()

      def test_something(self):
         print "Hello world!"
         self.assertEqual(self.stdout.getvalue(), 'Hello world!\n')


There's a function for checking partial calls to a ``mock`` :

.. code:: python

  def test_partial_calls(self):
      mock = Mock()
      mock(1, kwarg=2)

      self.assertSoftCalledWith(mock, 1)           # OK
      self.assertSoftCalledWith(mock, kwarg=2)     # OK
      self.assertSoftCalledWith(mock, 1, kwarg=2)  # OK
      self.assertSoftCalledWith(mock, 2)           # FAIL
      self.assertSoftCalledWith(mock, kwarg=1)     # FAIL

Lastly, a little helper function for checking sizes:

.. code:: python

  def test_some_size(self):
      self.assertSize([1, 2, 3], 3)
