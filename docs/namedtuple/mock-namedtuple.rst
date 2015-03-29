.. _namedtuple/mock-namedtuple:

=====================
Mocks for namedtuples
=====================

If you are using a :py:class:`collections.namedtuple` as function arguments,
and someone adds a field to it, all tests using that namedtuple will break,
*even* those unrelated to the new field.

:py:func:`~pignacio_scripts.namedtuple.mock_nt.mock_namedtuple_class` tries to
fix this problem enabling the creation of partially filled tuples.

.. code:: python

  >>> # Given a tuple
  >>> import collections
  >>> Tuple = collectionsd.namedtuple('Tuple', ['a', 'b', 'c'])
  >>>
  >>> # You can mock it
  >>> from pignacio_scripts.namedtuple import mock_namedtuple_class
  >>> MockTuple = mock_namedtuple_class(Tuple)
  >>>
  >>> # And create it without specifying all the fields
  >>> mock = MockTuple(a=3)
  >>> mock.a
  3
  >>>
  >>> # Missing fields raise AttributeError
  >>> mock.b
  Traceback (most recent call last):
    [...]
  AttributeError: Missing 'b' field in 'Tuple' mock. (id=140371982628528)

``_replace`` works, even on missing fields (as long as you don't read from
them beforhand).

.. code:: python

  >>> mock = MockTuple(a=3)
  >>> mock._replace(b=3).b
  3

You can also mock a single instance without mocking the class, using
:py:func:`~pignacio_scripts.namedtuple.mock_nt.mock_namedtuple`.

.. code:: python

  >>> from pignacio_scripts.namedtuple import mock_namedtuple
  >>> mock = mock_namedtuple(Tuple, a=3)

