.. _terminal/color:

====================================
Adding color to your terminal output
====================================

You can add color to the terminal output of your scripts using the functions
in the :py:mod:`~pignacio_scripts/terminal/color` module.

The module has 16 functions for the bright and normal versions of the 8
terminal colors.

They only change the fore color of the text.

.. code:: python

  >>> from pignacio_scripts.terminal.color import green
  >>> green('This text is green')
  u'\x1b[32mThis text is green\x1b[0m'
  >>> print green('This text is green')
  This text is green

