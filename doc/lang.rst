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
* for
* return

Operators
---------

* boolean: and, or
* \+ - * / (where applicable)
* :ref:`comparisons`  < <= == != >= > 
* len (as applicable)
* [] (list and dict indexing)

What is not supported
=====================

* Variable arguments and keywork arguments (`*args` and `**kwargs`).
  Note that methods :ref:`added via Java <adding_methods>` can take
  variable numbers of arguments.
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
