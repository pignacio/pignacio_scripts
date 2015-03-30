.. _namedtuple/namedtuple-with-defaults:

==============================
Namedtuple with default values
==============================

A namedtuple extension that sets default values.

Code is easier than words:

.. code:: python

  >>> from pignacio_scripts.namedtuple import namedtuple_with_defaults
  >>>
  >>> MyTuple = namedtuple_with_defaults('MyTuple', ['a', 'b'], defaults={'b': 5})
  >>>
  >>> mytuple = MyTuple(a=4)
  >>> mytuple.a
  4
  >>> mytuple.b
  5
  >>> MyTuple(a=1, b=2).b
  2

Construction fails if one of the fields without default is missing:

.. code:: python

  >>> mytuple = MyTuple(b=3)
  Traceback (most recent call last):
    [..]
  ValueError: Missing argument for namedtuple: 'a'

If you need a mutable default value (``[]``, ``{}``, etc.), you can pass a
function with no arguments that returns the defaults.

.. code:: python

  >>> MyTuple = namedtuple_with_defaults(
          'MyTuple', ['value', 'error_list'],
          defaults=lambda: {'error_list': []})
  >>>
  >>> MyTuple(value=3)
  MyTuple(value=3, error_list=[])

