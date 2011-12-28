Syntax/type support
*******************

The goal is to support a useful subset of Python syntax and keep the
resulting files small.  If you want fuller Python support then
consider using `Jython <http://www.jython.org>`__ instead.

What is supported
=================

Types
-----

* int
* string (unicode only)
* list
* dict
* bool (:ref:`note <booleans>`)
* None
* tuple (note: treated as list and mutable)

Keywords
--------

* def (new methods)
* if
* while
* for  iterate over list members and dict keys
* return
* del

Operators
---------

* boolean: and, or
* \+ - * / % (where applicable for types)
* :ref:`comparisons`  < <= == != >= > 
* len (as applicable)
* [] (list and dict indexing)
* [from:to] list slicing (step not supported)

Beware
======

It is generally a bad idea to modify lists or dicts while iterating
over them.  (This is true of regular Python too.)

The `str % list` (% operator) just calls :jdoc:`String.format
<java/lang/String.html#format(java.lang.String, java.lang.Object...)>`
which uses different rules than Python's equivalent.  For example
Python will complain if too many arguments are provided while
String.format doesn't.

What is not supported
=====================

* Variable arguments and keyword arguments (`*args` and `**kwargs`).
  Note that methods :ref:`added via Java <adding_methods>` can take
  variable numbers of arguments.  You can call :func:`apply` to call
  a function with a list of arguments.
* Classes
* Decorators
* Threads
* Exceptions
* More than one source file/module
* Generators
* Import
* With
* List comprehensions
* Tuple unpacking.  For example::

    for x,y in z:
        pass
* Floating point
* Bytes type

Use Jython if you want more than mini-Python
