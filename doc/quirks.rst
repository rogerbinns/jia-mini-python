Quirks and differences
**********************

.. _comparisons:

:index:`Comparisons`
--------------------

Comparisons will always succeed.  This is to ensure you can sort any
list and not have to worry about members being different types.

Where the items being compared are the same type then the logical
comparison is performed.  For dictionaries that are not equal the
:func:`id` is used as ordering doesn't make sense.

When the types differ then there is still an absolute ordering (eg all
lists come after all dicts).  This matches the behaviour of Python 2,
although the ordering of unrelated types may differ (the type name is
used for the comparison).  In Python 3 comparing unrelated types
results in an exception.

.. _tuples:

Tuples
------

Tuples are not supported.  Where they are encountered in your source
they are treated as though you specified a list.  This means you can
also mutate them unlike regular Python.

Dictionary keys
---------------

Python only allows immutable types as keys, for example string,
numbers and tuples.  This implementation will let you use any type
including mutable lists, dicts etc as the key.  Note that altering a
list/dict after using it as a key will make it impossible to find the key
again (the hash code will have changed) and could lead to exceptions.

.. _booleans:

Booleans
--------

Python treats True as the integer 1 and False as zero in several
places::

   >>> 3+True-4*False
   4
   >>> 1==True
   True
   >>> True>-1
   True

It is currently an error in Java Mini Python to do so.  You can use
:func:`int` to convert a bool to 1/0.

Concurrent container modification/iteration
-------------------------------------------

It is generally a bad idea to modify lists or dicts while iterating
over them.  (This is true of regular Python too.)

String format
-------------

The `str % list` (% operator) just calls :jdoc:`String.format
<java/lang/String.html#format(java.lang.String, java.lang.Object...)>`
which uses different rules than Python's equivalent.  For example
Python will complain if too many arguments are provided while
String.format doesn't.
