Quirks and differences
**********************

.. _comparisons:

:index:`Comparisons`
--------------------

Comparisons that have order (<, > etc) only work when the values have
the same type.  You get a TypeError otherwise.  This is the same
behaviour as Python 3.  (In Python 2 there is absolute ordering
between types: for example lists come after dictionaries.)

This also applies to lists where member by member comparisons are
made.  For example this will give an error::

   [ 3 ] < [ "4" ]

However this will not give an error as the second elements are not
compared::

   [ 3 ] < [ 3, "5" ]

Dictionary keys
---------------

Python only allows immutable types as keys, for example string,
numbers and tuples.  This implementation will also let you use mutable
lists as the key.
